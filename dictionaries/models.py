from django.db import models


class Krp(models.Model):
    krp_code = models.CharField(max_length=10, unique=True, verbose_name="Код КРП")
    krp_name = models.CharField(max_length=512, verbose_name="КРП название")
    
    def __str__(self):
        return f"{self.krp_name}"

    class Meta:
        db_table = "krp"
        verbose_name = "Размер предприятия"
        verbose_name_plural = "Размер предприятия"
    

class Kse(models.Model):
    kse_code = models.CharField(max_length=10, unique=True, verbose_name="Код КСЕ")
    kse_name = models.CharField(max_length=512, verbose_name="КСЕ название")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительский сектор",
    )

    def __str__(self):
        return f"{self.kse_name}"

    class Meta:
        db_table = "kse"
        verbose_name = "Экономические сектора"
        verbose_name_plural = "Экономические сектора"


class Kfc(models.Model):
    kfc_code = models.CharField(max_length=10, unique=True, verbose_name="Код КФС")
    kfc_name = models.CharField(max_length=512, verbose_name="КФС название")


    def __str__(self):
        return f"{self.kfc_name}"

    class Meta:
        db_table = "kfc"
        verbose_name = "Форма собственности"
        verbose_name_plural = "Форма собственности"


class Kato(models.Model):
    kato_code = models.CharField(max_length=12, unique=True, verbose_name="Код КАТО")
    kato_name = models.CharField(max_length=512, verbose_name="КАТО название")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительский КАТО"
    )

    def __str__(self):
        return f"{self.kato_name}"

    class Meta:
        db_table = "kato"
        verbose_name = "Административно-территориальные объекты (КАТО)"
        verbose_name_plural = "Административно-территориальные объекты (КАТО)"


class Oked(models.Model):
    oked_code = models.CharField(max_length=10, unique=True, verbose_name="Код ОКЭД")
    oked_name = models.CharField(max_length=512, verbose_name="ОКЭД название")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительский ОКЭД"
    )

    def __str__(self):
        return f"{self.oked_name}"

    class Meta:
        db_table = "oked"
        verbose_name = "Виды экономической деятельности (ОКЭД)"
        verbose_name_plural = "Виды экономической деятельности (ОКЭД)"


class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "industries"
        verbose_name = "Отрасль"
        verbose_name_plural = "Отрасли"
        
        ordering = ("name",)


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"



class Tnved(models.Model):
    tn_ved_code = models.CharField(max_length=10, unique=True, verbose_name="Код ТН ВЭД")
    tn_ved_name = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Наименование ТН ВЭД")

    def __str__(self):
        return f"{self.tn_ved_code} — {self.tn_ved_name}"

    class Meta:
        db_table = "tnved"
        verbose_name = "ТН ВЭДы"
        verbose_name_plural = "ТН ВЭДы"


class CompanyProduct(models.Model):
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE, related_name="products", verbose_name="Организация")
    tnved = models.ForeignKey("dictionaries.Tnved", on_delete=models.PROTECT, related_name="companies", verbose_name="ТН ВЭД")

    def __str__(self):
        return f"{self.company} — {self.tnved}"

    class Meta:
        db_table = "company_products"
        verbose_name = "Продукция компании"
        verbose_name_plural = "Продукция компаний"
        unique_together = ("company", "tnved")