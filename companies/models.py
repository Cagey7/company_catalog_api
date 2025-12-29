from django.db import models


class Company(models.Model):
    name_ru = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Название организации на русском")
    name_kz = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Название организации на казахском")
    register_date = models.DateField(null=True, blank=True, verbose_name="Время создания организации")
    ceo = models.CharField(max_length=512, null=True, blank=True, verbose_name="Руководитель организации")
    company_bin = models.CharField(max_length=12, unique=True, verbose_name="БИН")
    pay_nds = models.BooleanField(null=True, verbose_name="Плательщик НДС")
    tax_risk = models.CharField(max_length=32, null=True, verbose_name="Степень риска налогоплательщика")
    address = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Адрес организации на русском")
    phone_number = models.CharField(max_length=128, null=True, blank=True, verbose_name="Номер телефона")
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Электронная почта")
    krp = models.ForeignKey("dictionaries.Krp", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КРП")
    kse = models.ForeignKey("dictionaries.Kse", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КСЕ")
    kfc = models.ForeignKey("dictionaries.Kfc", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КФС")
    kato = models.ForeignKey("dictionaries.Kato", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КАТО")
    product = models.ManyToManyField("dictionaries.Product", blank=True)
    industry = models.ForeignKey("dictionaries.Industry", on_delete=models.PROTECT, null=True, blank=True)
    primary_oked = models.ForeignKey("dictionaries.Oked", on_delete=models.PROTECT, null=True, blank=True, related_name="primary_oked", verbose_name="ОКЭД")
    secondary_okeds = models.ManyToManyField("dictionaries.Oked", blank=True, related_name="secondary_okeds")
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name_ru}"

    class Meta:
        db_table = "companies"
        verbose_name = "Компании"
        verbose_name_plural = "Компании"


class CompanyContact(models.Model):
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE, related_name="contacts", verbose_name="Организация")
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="ФИО")
    position = models.CharField(max_length=255, null=True, blank=True, verbose_name="Должность")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Телефон")
    is_mailing_contact = models.BooleanField(default=False, verbose_name="Использовать для рассылок")
    notes = models.TextField(null=True, blank=True, verbose_name="Примечания")

    def __str__(self):
        return self.full_name or self.label or self.email or self.phone or f"Контакт #{self.id}"

    class Meta:
        db_table = "company_contacts"
        verbose_name = "Контакт компании"
        verbose_name_plural = "Контакты компаний"