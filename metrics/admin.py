from django.contrib import admin
from .models import Taxes, Nds, GosZakupSupplier, GosZakupCustomer


class BaseCompanyYearValueAdmin(admin.ModelAdmin):
    list_display = ("company", "company_bin", "year", "value")
    list_select_related = ("company",)
    list_filter = ("year",)
    search_fields = (
        "company__company_bin",
        "company__name_ru",
        "company__name_kz",
        "company__ceo",
    )
    ordering = ("-year", "company__name_ru")

    @admin.display(description="БИН", ordering="company__company_bin")
    def company_bin(self, obj):
        return obj.company.company_bin


@admin.register(Taxes)
class TaxesAdmin(BaseCompanyYearValueAdmin):
    pass


@admin.register(Nds)
class NdsAdmin(BaseCompanyYearValueAdmin):
    pass


@admin.register(GosZakupSupplier)
class GosZakupSupplierAdmin(BaseCompanyYearValueAdmin):
    pass


@admin.register(GosZakupCustomer)
class GosZakupCustomerAdmin(BaseCompanyYearValueAdmin):
    pass
