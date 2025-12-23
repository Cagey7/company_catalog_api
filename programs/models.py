from django.db import models
from companies.models import Company

class Program(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название программы")
    description = models.TextField(null=True, blank=True, verbose_name="Описание программы")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "programs"
        verbose_name = "Программа"
        verbose_name_plural = "Программы"


class ProgramParticipation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="program_participations", verbose_name="Организация")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="participants", verbose_name="Программа")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год участия")

    def __str__(self):
        return f"{self.company} — {self.program} ({self.year})"

    class Meta:
        db_table = "program_participation"
        verbose_name = "Участие в программе"
        verbose_name_plural = "Участие в программах"
        unique_together = ("company", "program", "year")
