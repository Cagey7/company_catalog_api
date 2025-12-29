from django.contrib import admin, messages
from django.db.models import Count
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html

from .models import Company, CompanyContact
from dictionaries.models import Industry

from .services.prg_loader import load_company_data_by_bin, CompanyLoadError


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


class CompanyContactInline(admin.TabularInline):
    model = CompanyContact
    extra = 1
    fields = (
        "full_name",
        "position",
        "email",
        "phone",
        "is_mailing_contact",
        "notes",
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.NEVER

    list_display = (
        "name_ru",
        "company_bin",
        "industry",
        "primary_oked",
        "kato",
        "updated",
    )

    list_filter = (
        IndustryUsedFilter,
        "primary_oked",
        "kfc",
        "kse",
        "krp",
        "kato",
        "product",
    )

    search_fields = (
        "name_ru",
        "name_kz",
        "company_bin",
        "ceo",
        "phone_number",
        "email",
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
    )

    filter_horizontal = ("secondary_okeds", "product")

    readonly_fields = ("updated", "load_data_button")

    inlines = (CompanyContactInline,)

    fieldsets = (
        ("Основная информация", {
            "fields": (
                "name_ru",
                "name_kz",
                "company_bin",
                "register_date",
                "ceo",
                "phone_number",
                "email",
                "load_data_button",
            )
        }),
        ("Адрес", {
            "fields": (
                "address",
                "kato",
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
            )
        }),
        ("Системные поля", {
            "fields": ("updated",)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/load-data/",
                self.admin_site.admin_view(self.load_data_view),
                name="companies_company_load_data",
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


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "full_name",
        "position",
        "email",
        "phone",
        "is_mailing_contact",
    )
    search_fields = (
        "company__company_bin",
        "company__name_ru",
        "full_name",
        "email",
        "phone",
    )
    list_filter = ("is_mailing_contact",)
    autocomplete_fields = ("company",)
