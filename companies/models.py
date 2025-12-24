from django.db import models


class Company(models.Model):
    name_ru = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Название организации на русском")
    name_kz = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Название организации на казахском")
    register_date = models.DateField(null=True, verbose_name="Время создания организации")
    ceo = models.CharField(max_length=512, null=True, verbose_name="Руководитель организации")
    company_bin = models.CharField(max_length=12, unique=True, verbose_name="БИН")
    address = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Адрес организации на русском")
    phone_number = models.CharField(max_length=128, null=True, blank=True, verbose_name="Номер телефона")
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Электронная почта")
    krp = models.ForeignKey("Krp", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КРП")
    kse = models.ForeignKey("Kse", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КСЕ")
    kfc = models.ForeignKey("Kfc", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КФС")
    kato = models.ForeignKey("Kato", on_delete=models.PROTECT, null=True, blank=True, verbose_name="КАТО")
    product = models.ManyToManyField("Product", blank=True)
    industry = models.ForeignKey("Industry", on_delete=models.PROTECT, null=True)
    primary_oked = models.ForeignKey("Oked", on_delete=models.PROTECT, null=True, blank=True, related_name="primary_oked", verbose_name="ОКЭД")
    secondary_okeds = models.ManyToManyField("Oked", related_name="secondary_okeds")
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name_ru}"

    class Meta:
        db_table = "companies"
        verbose_name = "Компании"
        verbose_name_plural = "Компании"


class Krp(models.Model):
    krp_code = models.IntegerField(unique=True, verbose_name="КРП код")
    krp_name = models.CharField(max_length=512, verbose_name="КРП название")
    
    def __str__(self):
        return f"{self.krp_name}"

    class Meta:
        db_table = "krp"
        verbose_name = "Размер предприятия"
        verbose_name_plural = "Размер предприятия"
    

class Kse(models.Model):
    kse_code = models.IntegerField(unique=True, verbose_name="КСЕ код")
    kse_name = models.CharField(max_length=512, verbose_name="КСЕ название")

    def __str__(self):
        return f"{self.kse_name}"

    class Meta:
        db_table = "kse"
        verbose_name = "Экономические сектора"
        verbose_name_plural = "Экономические сектора"


class Kfc(models.Model):
    kfc_code = models.IntegerField(unique=True, verbose_name="КФС код")
    kfc_name = models.CharField(max_length=512, verbose_name="КФС название")

    def __str__(self):
        return f"{self.kfc_name}"

    class Meta:
        db_table = "kfc"
        verbose_name = "Форма собственности"
        verbose_name_plural = "Форма собственности"


class Kato(models.Model):
    kato_code = models.IntegerField(unique=True, verbose_name="КАТО коде")
    kato_name = models.CharField(max_length=512, verbose_name="КАТО название")
    
    def __str__(self):
        return f"{self.kato_name}"

    class Meta:
        db_table = "kato"
        verbose_name = "Административно-территориальные объекты (КАТО)"
        verbose_name_plural = "Административно-территориальные объекты (КАТО)"


class Oked(models.Model):
    oked_code = models.IntegerField(unique=True, verbose_name="ОКЭД код")
    oked_name = models.CharField(max_length=512, verbose_name="ОКЭД название")

    def __str__(self):
        return f"{self.oked_name}"

    class Meta:
        db_table = "oked"
        verbose_name = "Виды экономической деятельности (ОКЭД)"
        verbose_name_plural = "Виды экономической деятельности (ОКЭД)"


class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "industries"
        verbose_name = "Отрасль"
        verbose_name_plural = "Отрасли"


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"


class CompanyContact(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="contacts", verbose_name="Организация")
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


class Tnved(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Код ТН ВЭД")
    name_ru = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Наименование ТН ВЭД")

    def __str__(self):
        return f"{self.code} — {self.name_ru}"

    class Meta:
        db_table = "tnved"
        verbose_name = "ТН ВЭДы"
        verbose_name_plural = "ТН ВЭДы"


class CompanyProduct(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="products", verbose_name="Организация")
    tnved = models.ForeignKey(Tnved, on_delete=models.PROTECT, related_name="companies", verbose_name="ТН ВЭД")

    def __str__(self):
        return f"{self.company} — {self.tnved}"

    class Meta:
        db_table = "company_products"
        verbose_name = "Продукция компании"
        verbose_name_plural = "Продукция компаний"
        unique_together = ("company", "tnved")
