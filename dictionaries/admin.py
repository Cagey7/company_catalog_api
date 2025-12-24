from django.contrib import admin

from .models import (
    Krp, Kse, Kfc, Kato, Oked,
    Industry, Product, Tnved,
    CompanyProduct,
)


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


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Tnved)
class TnvedAdmin(admin.ModelAdmin):
    list_display = ("code", "name_ru")
    search_fields = ("code", "name_ru")


# Если CompanyProduct у тебя реально лежит в dictionaries/models.py — регистрируй тут:
@admin.register(CompanyProduct)
class CompanyProductAdmin(admin.ModelAdmin):
    list_display = ("company", "tnved")
    search_fields = ("company__name_ru", "company__company_bin", "tnved__code", "tnved__name_ru")
    autocomplete_fields = ("company", "tnved")
