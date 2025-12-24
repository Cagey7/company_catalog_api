from django.contrib import admin

from .models import Company, CompanyContact

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
    list_display = (
        "name_ru",
        "company_bin",
        "industry",
        "primary_oked",
        "kato",
        "updated",
    )

    list_filter = (
        "industry",
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
    list_display = ("company", "full_name", "position", "email", "phone", "is_mailing_contact")
    search_fields = ("company__name_ru", "company__company_bin", "full_name", "email", "phone")
    list_filter = ("is_mailing_contact",)
    autocomplete_fields = ("company",)
