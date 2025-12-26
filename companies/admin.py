from django.contrib import admin
from django.db.models import Count

from .models import Company, CompanyContact
from dictionaries.models import Industry


class IndustryUsedFilter(admin.SimpleListFilter):
    title = "Отрасль"
    parameter_name = "industry"

    def lookups(self, request, model_admin):
        """
        Показываем только те Industry,
        которые используются хотя бы в одной Company
        """
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

    readonly_fields = ("updated",)

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
