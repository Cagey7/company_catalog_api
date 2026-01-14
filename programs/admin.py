from django.contrib import admin


from .models import Program, ProgramParticipation
from companies.models import Company

class ProgramParticipationInline(admin.TabularInline):
    model = ProgramParticipation
    extra = 1
    autocomplete_fields = ("company",)
    fields = ("company", "year")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = (ProgramParticipationInline,)


@admin.register(ProgramParticipation)
class ProgramParticipationAdmin(admin.ModelAdmin):
    list_display = ("company", "program", "year")
    list_filter = ("program", "year")
    search_fields = ("company__name_ru", "company__company_bin", "program__name")
    autocomplete_fields = ("company", "program")
