from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from django.urls import path

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

    change_list_template = "admin/program_participation_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "export-xlsx/",
                self.admin_site.admin_view(self.export_xlsx),
                name="program_participation_export_xlsx",
            ),
        ]
        return custom_urls + urls

    def export_xlsx(self, request):
        cl = self.get_changelist_instance(request)
        participation_qs = cl.get_queryset(request)

        # Берём уникальные компании из отфильтрованных участий
        company_ids = participation_qs.values_list("company_id", flat=True).distinct()

        companies_qs = (
            Company.objects
            .filter(id__in=company_ids)
            .select_related("industry", "kato")
            .prefetch_related("contacts__emails", "contacts__phones")
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Companies"

        ws.append(["Company name (RU)", "Industry", "Region (KATO)", "Contacts"])

        def format_contacts(company):
            lines = []
            for c in company.contacts.all():
                name = c.full_name or ""
                pos = c.position or ""
                header = " — ".join([x for x in [name, pos] if x]).strip()

                phones = [p.phone for p in c.phones.all()]
                emails = [e.email for e in c.emails.all()]

                parts = []
                if phones:
                    parts.append("Phones: " + ", ".join(phones))
                if emails:
                    parts.append("Emails: " + ", ".join(emails))

                if header and parts:
                    lines.append(f"{header}: " + " | ".join(parts))
                elif header:
                    lines.append(header)
                elif parts:
                    lines.append(" | ".join(parts))

            return "\n".join(lines) if lines else ""

        for company in companies_qs:  # без iterator — безопасно с prefetch
            industry = getattr(company.industry, "name", None) if company.industry else None
            region = str(company.kato) if company.kato else None

            ws.append([company.name_ru, industry, region, format_contacts(company)])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="companies.xlsx"'
        wb.save(response)
        return response

