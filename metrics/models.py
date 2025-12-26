from django.db import models
from companies.models import Company


class Taxes(models.Model):
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания", related_name="taxes")

    class Meta:
        db_table = "taxes"
        verbose_name = "Налоги"
        verbose_name_plural = "Налоги"

class Nds(models.Model):
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания", related_name="nds")

    class Meta:
        db_table = "nds"
        verbose_name = "НДС"
        verbose_name_plural = "НДС"

class GosZakupSupplier(models.Model):
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания", related_name="goszakupsupplier")

    class Meta:
        db_table = "gos_zakup_supplier"
        verbose_name = "Гос. закупки (как поставщик)"
        verbose_name_plural = "Гос. закупки (как поставщик)"

class GosZakupCustomer(models.Model):
    year = models.IntegerField(verbose_name="Год")
    value = models.FloatField(verbose_name="Значение")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания", related_name="goszakupcustomer")

    class Meta:
        db_table = "gos_zakup_customer"
        verbose_name = "Гос. закупки (как закупщик)"
        verbose_name_plural = "Гос. закупки (как закупщик)"