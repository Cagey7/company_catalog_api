import re
from datetime import datetime
from urllib.parse import quote
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from requests import request
from .models import Company, CompanyContact, ContactEmail, ContactPhone, Certificate
from dictionaries.models import Industry, Kato, Oked, Krp, Product, Tnved, Country, Kse, Kfc
from programs.models import Program, ProgramParticipation, TEMParticipation, AccelerationParticipation
from django.http import HttpResponse, QueryDict
from urllib.parse import quote

from .services.excel_builder import excel_builder

from .services.prg_loader import load_company_data_by_bin, CompanyLoadError
from django.http import HttpResponse
from openpyxl import Workbook
from django.urls import path


class IndustryUsedFilter(admin.SimpleListFilter):
    title = "Отрасль"
    parameter_name = "industry"

    def lookups(self, request, model_admin):
        qs = (
            Industry.objects
            .annotate(company_count=Count("company"))
            .filter(company_count__gt=0)
            .order_by("name")
        )
        return [(i.id, i.name) for i in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(industry_id=self.value())
        return queryset


class ProgramParticipationDrilldownFilter(admin.SimpleListFilter):
    title = "Программы / Год участия"
    parameter_name = "program_part"  # один параметр в URL

    # Формат value:
    #   "p:<program_id>"                -> выбрана программа
    #   "py:<program_id>:<year>"        -> выбрана программа + год

    def lookups(self, request, model_admin):
        raw = request.GET.get(self.parameter_name)  # текущее значение

        # --- уровень 1: список программ ---
        if not raw or not raw.startswith("p:"):
            qs = (
                Program.objects
                .annotate(cnt=Count("participants"))
                .filter(cnt__gt=0)
                .order_by("name")
            )
            return [(f"p:{p.id}", p.name) for p in qs]

        # --- уровень 2: список годов для выбранной программы ---
        try:
            program_id = int(raw.split(":")[1])
        except (ValueError, IndexError):
            return []

        items = []
        items.append(("__back__", "⬆️ Назад к программам"))

        years = (
            ProgramParticipation.objects
            .filter(program_id=program_id)
            .exclude(year__isnull=True)
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )

        for y in years:
            items.append((f"py:{program_id}:{y}", str(y)))

        # Если у программы нет годов (все null) — можно дать “Без года”
        if len(items) == 1:
            items.append((f"py:{program_id}:__null__", "Без года"))

        return items

    def queryset(self, request, queryset):
        raw = self.value()
        if not raw:
            return queryset

        # кнопка "назад"
        if raw == "__back__":
            return queryset

        # выбран уровень "программа"
        if raw.startswith("p:"):
            try:
                program_id = int(raw.split(":")[1])
            except (ValueError, IndexError):
                return queryset
            return queryset.filter(
                program_participations__program_id=program_id
            ).distinct()

        # выбран уровень "программа + год"
        if raw.startswith("py:"):
            parts = raw.split(":")
            if len(parts) != 3:
                return queryset

            try:
                program_id = int(parts[1])
            except ValueError:
                return queryset

            year_part = parts[2]
            if year_part == "__null__":
                return queryset.filter(
                    program_participations__program_id=program_id,
                    program_participations__year__isnull=True,
                ).distinct()

            try:
                year = int(year_part)
            except ValueError:
                return queryset

            return queryset.filter(
                program_participations__program_id=program_id,
                program_participations__year=year,
            ).distinct()

        return queryset

class KatoDrilldownFilter(SimpleListFilter):
    title = "КАТО (проваливание)"
    parameter_name = "kato_node"

    def lookups(self, request, model_admin):
        """
        Показываем список детей текущего узла.
        Если узел не выбран — показываем корни.
        """
        node_id = request.GET.get(self.parameter_name)

        current = None
        if node_id:
            try:
                current = Kato.objects.only("id", "parent_id").get(pk=node_id)
            except Kato.DoesNotExist:
                current = None

        items = []

        # кнопка "вверх"
        if current and current.parent_id:
            items.append((str(current.parent_id), "⬆️ Вверх"))

        # дети текущего узла (или корни)
        if current:
            qs = Kato.objects.filter(parent_id=current.id).order_by("kato_name")
        else:
            qs = Kato.objects.filter(parent__isnull=True).order_by("kato_name")

        for k in qs:
            items.append((str(k.id), k.kato_name))

        return items

    def queryset(self, request, queryset):
        """
        Когда выбран узел — показываем компании внутри этого узла:
        kato.path startswith выбранный.path
        """
        node_id = self.value()
        if not node_id:
            return queryset

        try:
            selected = Kato.objects.only("path").get(pk=node_id)
        except Kato.DoesNotExist:
            return queryset

        return queryset.filter(kato__path__startswith=selected.path)


class OkedDrilldownFilter(SimpleListFilter):
    title = "ОКЭД (проваливание)"
    parameter_name = "oked_node"

    def lookups(self, request, model_admin):
        """
        Показываем список детей текущего узла.
        Если узел не выбран — показываем корни.
        """
        node_id = request.GET.get(self.parameter_name)

        current = None
        if node_id:
            try:
                current = Oked.objects.only("id", "parent_id").get(pk=node_id)
            except Oked.DoesNotExist:
                current = None

        items = []

        # кнопка "вверх"
        if current and current.parent_id:
            items.append((str(current.parent_id), "⬆️ Вверх"))

        # дети текущего узла (или корни)
        if current:
            qs = Oked.objects.filter(parent_id=current.id).order_by("oked_name")
        else:
            qs = Oked.objects.filter(parent__isnull=True).order_by("oked_name")

        for o in qs:
            items.append((str(o.id), o.oked_name))

        return items

    def queryset(self, request, queryset):
        """
        Когда выбран узел — показываем компании внутри этого узла:
        primary_oked.path startswith выбранный.path
        """
        node_id = self.value()
        if not node_id:
            return queryset

        try:
            selected = Oked.objects.only("path").get(pk=node_id)
        except Oked.DoesNotExist:
            return queryset

        # ВАЖНО: поле в Company называется primary_oked (FK на Oked)
        return queryset.filter(primary_oked__path__startswith=selected.path)

class KrpDrilldownFilter(SimpleListFilter):
    title = "КРП (проваливание)"
    parameter_name = "krp_node"

    def lookups(self, request, model_admin):
        """
        Показываем список детей текущего узла.
        Если узел не выбран — показываем корни.
        """
        node_id = request.GET.get(self.parameter_name)

        current = None
        if node_id:
            try:
                current = Krp.objects.only("id", "parent_id").get(pk=node_id)
            except Krp.DoesNotExist:
                current = None

        items = []

        # кнопка "вверх"
        if current and current.parent_id:
            items.append((str(current.parent_id), "⬆️ Вверх"))

        # дети текущего узла (или корни)
        if current:
            qs = Krp.objects.filter(parent_id=current.id).order_by("krp_name")
        else:
            qs = Krp.objects.filter(parent__isnull=True).order_by("krp_name")

        for r in qs:
            items.append((str(r.id), r.krp_name))

        return items

    def queryset(self, request, queryset):
        """
        Когда выбран узел — показываем компании внутри этого узла:
        krp.path startswith выбранный.path
        """
        node_id = self.value()
        if not node_id:
            return queryset

        try:
            selected = Krp.objects.only("path").get(pk=node_id)
        except Krp.DoesNotExist:
            return queryset

        return queryset.filter(krp__path__startswith=selected.path)


class ProductDrilldownFilter(SimpleListFilter):
    title = "Товары (проваливание)"
    parameter_name = "product_node"

    def lookups(self, request, model_admin):
        node_id = request.GET.get(self.parameter_name)

        current = None
        if node_id:
            try:
                current = Product.objects.only("id", "parent_id").get(pk=node_id)
            except Product.DoesNotExist:
                current = None

        items = []

        if current and current.parent_id:
            items.append((str(current.parent_id), "⬆️ Вверх"))

        if current:
            qs = Product.objects.filter(parent_id=current.id).order_by("name")
        else:
            qs = Product.objects.filter(parent__isnull=True).order_by("name")

        for p in qs:
            items.append((str(p.id), p.name))

        return items

    def queryset(self, request, queryset):
        node_id = self.value()
        if not node_id:
            return queryset

        try:
            selected = Product.objects.only("path").get(pk=node_id)
        except Product.DoesNotExist:
            return queryset

        return queryset.filter(product__path__startswith=selected.path).distinct()


class AccelerationYearFilter(admin.SimpleListFilter):
    title = "Акселерация: год"
    parameter_name = "acc_year"

    def lookups(self, request, model_admin):
        years = (
            AccelerationParticipation.objects
            .exclude(year__isnull=True)
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        return [(str(y), str(y)) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(acceleration_participations__year=int(self.value())).distinct()
        return queryset


class TEMDrilldownFilter(admin.SimpleListFilter):
    title = "ТЭМ: год / страна"
    parameter_name = "tem_part"

    # Формат value:
    #   "y:<year>"              -> выбран год
    #   "yc:<year>:<country>"  -> выбран год + страна

    def lookups(self, request, model_admin):
        raw = request.GET.get(self.parameter_name)

        # -------- уровень 1: годы --------
        if not raw or not raw.startswith("y:"):
            years = (
                TEMParticipation.objects
                .values_list("year", flat=True)
                .distinct()
                .order_by("-year")
            )
            return [(f"y:{y}", str(y)) for y in years]

        # -------- уровень 2: страны для выбранного года --------
        try:
            year = int(raw.split(":")[1])
        except (ValueError, IndexError):
            return []

        items = []
        items.append(("__back__", "⬆️ Назад к годам"))

        countries = (
            Country.objects
            .filter(trade_missions__year=year)
            .distinct()
            .order_by("name")
        )

        for c in countries:
            items.append((f"yc:{year}:{c.id}", c.name))

        return items

    def queryset(self, request, queryset):
        raw = self.value()
        if not raw:
            return queryset

        if raw == "__back__":
            return queryset

        # выбран год
        if raw.startswith("y:"):
            try:
                year = int(raw.split(":")[1])
            except (ValueError, IndexError):
                return queryset
            return queryset.filter(trade_missions__year=year).distinct()

        # выбран год + страна
        if raw.startswith("yc:"):
            try:
                _, year, country_id = raw.split(":")
                return queryset.filter(
                    trade_missions__year=int(year),
                    trade_missions__country_id=int(country_id),
                ).distinct()
            except ValueError:
                return queryset

        return queryset


# -------------------------
# Inlines for contact details
# -------------------------
class ContactEmailInline(admin.TabularInline):
    model = ContactEmail
    extra = 0
    fields = ("email", "is_primary", "is_mailing")
    ordering = ("-is_primary", "-is_mailing", "id")


class ContactPhoneInline(admin.TabularInline):
    model = ContactPhone
    extra = 0
    fields = ("phone", "is_primary", "is_mailing")
    ordering = ("-is_primary", "-is_mailing", "id")

class ProgramParticipationInline(admin.TabularInline):
    model = ProgramParticipation
    extra = 0
    autocomplete_fields = ("program",)   # удобно, если программ много
    fields = ("program", "year")

class AccelerationParticipationInline(admin.TabularInline):
    model = AccelerationParticipation
    extra = 0
    fields = ("year",)


class TEMParticipationInline(admin.TabularInline):
    model = TEMParticipation
    extra = 0
    autocomplete_fields = ("country",)   # удобно, если стран много
    fields = ("country", "year")
# -------------------------
# Filters for mailing flags
# -------------------------
class HasMailingEmailFilter(admin.SimpleListFilter):
    title = "Есть email для рассылки"
    parameter_name = "has_mailing_email"

    def lookups(self, request, model_admin):
        return [("1", "Да"), ("0", "Нет")]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(emails__is_mailing=True).distinct()
        if self.value() == "0":
            return queryset.exclude(emails__is_mailing=True).distinct()
        return queryset


class HasMailingPhoneFilter(admin.SimpleListFilter):
    title = "Есть телефон для рассылки"
    parameter_name = "has_mailing_phone"

    def lookups(self, request, model_admin):
        return [("1", "Да"), ("0", "Нет")]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(phones__is_mailing=True).distinct()
        if self.value() == "0":
            return queryset.exclude(phones__is_mailing=True).distinct()
        return queryset


# -------------------------
# CompanyContact Admin
# -------------------------
@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "full_name",
        "position",
        "primary_email",
        "primary_phone",
        "mailing_emails",
        "mailing_phones",
    )

    search_fields = (
        "company__company_bin",
        "company__name_ru",
        "full_name",
        "position",
        "emails__email",
        "phones__phone",
    )

    list_filter = (HasMailingEmailFilter, HasMailingPhoneFilter)
    autocomplete_fields = ("company",)
    inlines = (ContactEmailInline, ContactPhoneInline)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("company").prefetch_related("emails", "phones")

    @admin.display(description="Primary Email")
    def primary_email(self, obj: CompanyContact):
        e = obj.emails.filter(is_primary=True).first() or obj.emails.first()
        return e.email if e else "-"

    @admin.display(description="Primary Phone")
    def primary_phone(self, obj: CompanyContact):
        p = obj.phones.filter(is_primary=True).first() or obj.phones.first()
        return p.phone if p else "-"

    @admin.display(description="Emails для рассылки")
    def mailing_emails(self, obj: CompanyContact):
        emails = [e.email for e in obj.emails.all() if e.is_mailing]
        return ", ".join(emails) if emails else "-"

    @admin.display(description="Телефоны для рассылки")
    def mailing_phones(self, obj: CompanyContact):
        phones = [p.phone for p in obj.phones.all() if p.is_mailing]
        return ", ".join(phones) if phones else "-"


# -------------------------
# Company Inline: show contacts (no nested inlines)
# -------------------------
class CompanyContactInline(admin.TabularInline):
    model = CompanyContact
    extra = 0
    can_delete = False

    fields = ("contact_link", "primary_phone", "primary_email")
    readonly_fields = ("contact_link", "primary_phone", "primary_email")
    show_change_link = False

    @admin.display(description="Контакт")
    def contact_link(self, obj: CompanyContact):
        if not obj or not obj.pk:
            return "-"
        url = reverse("admin:companies_companycontact_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj))

    @admin.display(description="Телефон")
    def primary_phone(self, obj: CompanyContact):
        if not obj or not obj.pk:
            return "-"
        p = obj.phones.filter(is_primary=True).first() or obj.phones.order_by("id").first()
        return p.phone if p else "-"

    @admin.display(description="Email")
    def primary_email(self, obj: CompanyContact):
        if not obj or not obj.pk:
            return "-"
        e = obj.emails.filter(is_primary=True).first() or obj.emails.order_by("id").first()
        return e.email if e else "-"


# -------------------------
# Company Admin
# -------------------------
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.NEVER

    list_display = (
        "name_ru",
        "company_bin",
        "updated",
    )

    list_filter = (
        IndustryUsedFilter,
        KatoDrilldownFilter,
        OkedDrilldownFilter,
        KrpDrilldownFilter,
        ProgramParticipationDrilldownFilter,
        ProductDrilldownFilter,
        AccelerationYearFilter,
        TEMDrilldownFilter,
        "kfc",
    )


    search_fields = (
        "name_ru",
        "name_kz",
        "company_bin",
        "ceo"
    )

    autocomplete_fields = (
        "krp",
        "kse",
        "kfc",
        "kato",
        "industry",
        "primary_oked",
        "secondary_okeds",
        "product",
        "certificates",
        "tnveds", 
    )

    filter_horizontal = ("secondary_okeds", "product", "certificates", "tnveds")

    # ✅ добавили readonly поле региона
    readonly_fields = ("updated", "load_data_button", "kato_region")

    inlines = (
        CompanyContactInline,
        ProgramParticipationInline,
        AccelerationParticipationInline,
        TEMParticipationInline,
    )

    fieldsets = (
        ("Основная информация", {
            "fields": (
                "name_ru",
                "name_kz",
                "company_bin",
                "register_date",
                "ceo",
                "product_description",
                "load_data_button",
            )
        }),
        ("Адрес", {
            "fields": (
                "address",
                "kato",
                "kato_region",  # ✅ показываем регион
            )
        }),
        ("Классификаторы", {
            "fields": (
                "krp",
                "kse",
                "kfc",
                "industry",
                "primary_oked",
                "secondary_okeds",
                "product",
                "tnveds",
                "certificates",
            )
        }),
        ("Системные поля", {
            "fields": ("updated",)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # базовая оптимизация: подтягиваем kato одним join
        return (
            qs.select_related("kato", "industry", "primary_oked", "kfc", "kse", "krp")
            .prefetch_related(
                "certificates",
                "program_participations__program",
                "acceleration_participations",
                "trade_missions__country",
            )
        )


    @admin.display(description="Сертификаты")
    def certificates_list(self, obj: Company):
        names = list(obj.certificates.values_list("name", flat=True))
        return ", ".join(names) if names else "—"


    @admin.display(description="Область/Город")
    def kato_region(self, obj: Company):
        """
        Возвращает корневой КАТО (верхний parent) для выбранного obj.kato
        """
        k = getattr(obj, "kato", None)
        if not k:
            return "—"

        # Поднимаемся вверх по дереву
        while k.parent_id is not None:
            k = k.parent

        # Только название региона (корня)
        return k.kato_name
        # Если нужно "код — название", используй:
        # return f"{k.kato_code} — {k.kato_name}"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/load-data/",
                self.admin_site.admin_view(self.load_data_view),
                name="companies_company_load_data",
            ),
            path(
                "export-xlsx/",
                self.admin_site.admin_view(self.export_xlsx),
                name="companies_company_export_xlsx",
            ),
        ]
        return custom_urls + urls


    def load_data_button(self, obj):
        if not obj or not obj.pk:
            return "-"
        url = reverse("admin:companies_company_load_data", args=[obj.pk])
        return format_html('<a class="button" href="{}">Загрузить данные</a>', url)

    load_data_button.short_description = "Загрузка данных"

    def load_data_view(self, request, pk):
        company = get_object_or_404(Company, pk=pk)

        if not company.company_bin:
            self.message_user(request, "У компании не указан БИН.", level=messages.ERROR)
            return redirect(reverse("admin:companies_company_change", args=[pk]))

        try:
            result = load_company_data_by_bin(company.company_bin)
            msg = result.get("message", "Загрузка выполнена.")
            lvl = messages.SUCCESS if result.get("status") != "deleted" else messages.WARNING
            self.message_user(request, msg, level=lvl)

        except CompanyLoadError as e:
            self.message_user(request, f"Ошибка загрузки: {e}", level=messages.ERROR)

        except Exception as e:
            self.message_user(request, f"Неожиданная ошибка: {e}", level=messages.ERROR)

        return redirect(reverse("admin:companies_company_change", args=[pk]))


    change_list_template = "admin/program_participation_change_list.html"

    def export_xlsx(self, request):
        # 1) поля экспорта (до подмены GET!)
        export_fields = request.GET.getlist("fields")

        # 2) фильтры админки (спрятаны в hidden)
        changelist_filters = request.GET.get("_changelist_filters", "")

        # 3) подменяем GET, чтобы ChangeList применил фильтры "как на экране"
        request.GET = QueryDict(changelist_filters, mutable=False)

        # 4) queryset как в админке
        cl = self.get_changelist_instance(request)
        companies_qs = (
            cl.get_queryset(request)
            .select_related(
                "industry",
                "kato",
                "primary_oked",
                "kfc",
                "kse",
                "krp",
            )
            .prefetch_related(
                "contacts__emails",
                "contacts__phones",
                "certificates",
                "secondary_okeds",
                "product",
                "tnveds",
                "program_participations__program",
                "acceleration_participations",
                "trade_missions__country",
            )
        )

        # 5) осмысленные значения фильтров + красивое имя файла
        filters_info = get_export_filters_values(request)   # <- теперь это уже человекочитаемо
        print(filters_info)
        filename = build_export_filename(filters_info, prefix="companies")
        if not filename.lower().endswith(".xlsx"):
            filename += ".xlsx"

        # 6) собираем workbook
        wb = excel_builder(companies_qs, filters_info, export_fields)

        # 7) ответ
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        ascii_fallback = "companies.xlsx"
        quoted = quote(filename, safe="")

        response["Content-Disposition"] = (
            f'attachment; filename="{ascii_fallback}"; '
            f"filename*=UTF-8''{quoted}"
        )

        wb.save(response)
        return response


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


def get_export_filters_raw(request):
    return {
        k: v
        for k, v in request.GET.items()
        if v not in ("", None)
    }


def _first_present(raw, *keys):
    for k in keys:
        if k in raw:
            return raw[k]
    return None


def _get_name_by_pk(model, pk, field):
    return (
        model.objects
        .filter(pk=pk)
        .values_list(field, flat=True)
        .first()
    )


def get_export_filters_values(request):
    qd = request.GET

    def by_pk(model, pk, field=None):
        if not pk:
            return ""
        if field:
            return model.objects.filter(pk=pk).values_list(field, flat=True).first() or str(pk)
        obj = model.objects.filter(pk=pk).first()
        return str(obj) if obj else str(pk)

    def program_part_to_text(raw):
        # p:<program_id> или py:<program_id>:<year> или __back__
        if not raw or raw == "__back__":
            return ""
        if raw.startswith("p:"):
            _, pid = raw.split(":", 1)
            name = by_pk(Program, pid, "name")
            return f"«{name}»" if name else ""
        if raw.startswith("py:"):
            _, pid, year = raw.split(":", 2)
            name = by_pk(Program, pid, "name")
            return f"«{name}» ({year})" if name else ""
        return raw

    def tem_part_to_text(raw):
        # y:<year> или yc:<year>:<country_id> или __back__
        if not raw or raw == "__back__":
            return ""
        if raw.startswith("y:"):
            _, year = raw.split(":", 1)
            return year
        if raw.startswith("yc:"):
            _, year, cid = raw.split(":", 2)
            cname = by_pk(Country, cid, "name")
            return f"{year} — {cname}" if cname else year
        return raw

    FILTER_MAP = {
        "q": ("Поиск", lambda v: v),

        # ✅ реальные ключи твоих фильтров
        "industry": ("Отрасль", lambda v: by_pk(Industry, v, "name")),
        "kato_node": ("Регион", lambda v: by_pk(Kato, v, "kato_name")),
        "oked_node": ("ОКЭД", lambda v: by_pk(Oked, v, "oked_name")),
        "krp_node": ("КРП", lambda v: by_pk(Krp, v, "krp_name")),
        "product_node": ("Товар", lambda v: by_pk(Product, v, "name")),

        "program_part": ("Программа", program_part_to_text),
        "acc_year": ("Акселерация: год", lambda v: v),
        "tem_part": ("ТЭМ", tem_part_to_text),

        # ✅ обычный fk фильтр
        "kfc__id__exact": ("КФС", lambda v: by_pk(Kfc, v, "kfc_name")),
    }

    IGNORE_KEYS = {
        "p", "o", "ot", "all",
        "_popup", "_to_field",
        "_changelist_filters", "fields",
    }

    out = []
    for key in qd.keys():
        if key in IGNORE_KEYS:
            continue

        values = [v for v in qd.getlist(key) if v not in (None, "", "None")]
        if not values:
            continue

        if key in FILTER_MAP:
            label, conv = FILTER_MAP[key]
            human_values = [conv(v) for v in values]
            human_values = [hv for hv in human_values if hv]
            if human_values:
                out.append({"key": key, "label": label, "value": ", ".join(human_values)})
        else:
            out.append({"key": key, "label": key, "value": ", ".join(values)})

    return out



def build_export_filename(filters_info, prefix="companies"):
    """
    Строит осмысленное имя файла из человекочитаемых фильтров.
    """
    def clean(s: str) -> str:
        s = str(s)
        s = re.sub(r"\s+", " ", s).strip()
        s = s.replace("/", "-")
        s = re.sub(r"[^0-9A-Za-zА-Яа-яЁё _\-.]", "", s)
        s = s.replace(" ", "_")
        return s[:60]

    parts = [prefix]
    for item in filters_info:
        label = clean(item["label"])
        value = clean(item["value"])
        if label and value:
            parts.append(f"{label}-{value}")

    return "_".join(parts)