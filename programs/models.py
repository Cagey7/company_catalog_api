from django.db import models
from companies.models import Company
from dictionaries.models import Country


class Program(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название активности")
    description = models.TextField(null=True, blank=True, verbose_name="Описание активности")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "programs"
        verbose_name = "Активность"
        verbose_name_plural = "Активности"


class ProgramParticipation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="program_participations", verbose_name="Компания")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="participants", verbose_name="Активность компании")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год")

    def __str__(self):
        return f"{self.company} — {self.program} ({self.year})"

    class Meta:
        db_table = "program_participation"
        verbose_name = "Активность компании"
        verbose_name_plural = "Активности компаний"
        unique_together = ("company", "program", "year")


class AccelerationParticipation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="acceleration_participations", verbose_name="Компания")
    year = models.IntegerField(verbose_name="Год участия")

    def __str__(self):
        return f"{self.company} — Акселерация ({self.year})"

    class Meta:
        db_table = "acceleration_participation"
        verbose_name = "Участие в программе «Акселерация»"
        verbose_name_plural = "Участие в программе «Акселерация»"
        unique_together = ("company", "year")


class TEMParticipation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="trade_missions", verbose_name="Компания")
    year = models.IntegerField(verbose_name="Год проведения")
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="trade_missions",
        verbose_name="Страна ТЭМ"
    )

    def __str__(self):
        return f"{self.company} — ТЭМ {self.country} ({self.year})"

    class Meta:
        db_table = "trade_economic_mission"
        verbose_name = "Торгово-экономическая миссия"
        verbose_name_plural = "Торгово-экономические миссии"
        unique_together = ("company", "year", "country")
