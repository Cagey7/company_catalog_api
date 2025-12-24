from django.contrib import admin

from .models import (
    Company,
    CompanyContact,
    CompanyProduct,
    Krp,
    Kse,
    Kfc,
    Kato,
    Oked,
    Tnved,
    Product,
    Industry,
)


# ---------- Inlines (внутри Company) ----------

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


class CompanyTnvedInline(admin.TabularInline):
    """
    Это inline для CompanyProduct (company <-> tnved).
    Назвал по смыслу, чтобы не путаться с твоим M2M product.
    """
    model = CompanyProduct
    extra = 1
    autocomplete_fields = ("tnved",)


# ---------- Company ----------

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
        "product",  # M2M Product
    )

    search_fields = (
        "name_ru",
        "name_kz",
        "company_bin",
        "ceo",
        "phone_number",
        "email",
    )

    # autocomplete_fields можно ставить только на FK/M2M поля.
    # У тебя они все такие — включая product.
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

    # Если autocomplete вдруг снова капризничает на product (редко, но бывает),
    # тогда просто убери "product" из autocomplete_fields и оставь filter_horizontal ниже.
    filter_horizontal = ("secondary_okeds", "product")

    readonly_fields = ("updated",)

    inlines = (
        CompanyContactInline,
        CompanyTnvedInline,
    )

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
                "address_ru",
                "address_kz",
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
                "product",  # M2M Product
            )
        }),
        ("Системные поля", {
            "fields": ("updated",)
        }),
    )


# ---------- Справочники ----------

@admin.register(Krp)
class KrpAdmin(admin.ModelAdmin):
    list_display = ("krp_code", "krp_name")
    search_fields = ("krp_code", "krp_name")


@admin.register(Kse)
class KseAdmin(admin.ModelAdmin):
    list_display = ("kse_code", "kse_name")
    search_fields = ("kse_code", "kse_name")


@admin.register(Kfc)
class KfcAdmin(admin.ModelAdmin):
    list_display = ("kfc_code", "kfc_name")
    search_fields = ("kfc_code", "kfc_name")


@admin.register(Kato)
class KatoAdmin(admin.ModelAdmin):
    list_display = ("kato_code", "kato_name")
    search_fields = ("kato_code", "kato_name")


@admin.register(Oked)
class OkedAdmin(admin.ModelAdmin):
    list_display = ("oked_code", "oked_name")
    search_fields = ("oked_code", "oked_name")


@admin.register(Tnved)
class TnvedAdmin(admin.ModelAdmin):
    list_display = ("code", "name_ru")
    search_fields = ("code", "name_ru")


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ("name",)


# ---------- Отдельные админки (опционально) ----------

@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ("company", "full_name", "position", "email", "phone", "is_mailing_contact")
    search_fields = ("company__name_ru", "full_name", "email", "phone")
    list_filter = ("is_mailing_contact",)
    autocomplete_fields = ("company",)


@admin.register(CompanyProduct)
class CompanyProductAdmin(admin.ModelAdmin):
    list_display = ("company", "tnved")
    search_fields = ("company__name_ru", "tnved__code", "tnved__name_ru")
    autocomplete_fields = ("company", "tnved")
