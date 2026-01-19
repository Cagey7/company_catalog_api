from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from dictionaries.models import Kato  # важно: нужен доступ к модели КАТО


def build_excel_title(filters):
    print(filters)
    parts = []

    if filters.get("kato_node"):
        parts.append(filters["kato_node"])

    if filters.get("krp_node"):
        parts.append(filters["krp_node"])

    if filters.get("industry"):
        parts.append(filters["industry"])

    if filters.get("product_node"):
        parts.append(filters["product_node"])

    program = filters.get("program_part")
    if isinstance(program, dict):
        name = program.get("program")
        year = program.get("year")
        if name and year:
            parts.append(f"программа «{name}» ({year})")
        elif name:
            parts.append(f"программа «{name}»")

    if not parts:
        return "В данном списке представлены все компании без применения фильтров."

    return (
        "В данном списке представлены компании, отобранные по следующим параметрам: "
        + ", ".join(parts)
        + "."
    )


def format_kato_region_name(company):
    kato = getattr(company, "kato", None)
    if not kato or not getattr(kato, "kato_code", None):
        return ""

    code = str(kato.kato_code)

    if len(code) < 2:
        return ""

    region_code = code[:2] + ("0" * (len(code) - 2))

    region_name = (
        Kato.objects
        .filter(kato_code=region_code)
        .values_list("kato_name", flat=True)
        .first()
    )

    # если по какой-то причине не нашли — вернём хотя бы код
    return region_name or region_code


def excel_builder(companies_qs, filters_info):
    title_text = build_excel_title(filters_info)

    wb = Workbook()
    ws = wb.active
    ws.title = "Список компаний"

    # -------------------------
    # Styles
    # -------------------------
    title_font = Font(bold=True, size=14)
    header_font = Font(bold=True)
    header_fill = PatternFill("solid", fgColor="E6F0FF")
    thin = Side(style="thin", color="D0D0D0")
    border_thin = Border(left=thin, right=thin, top=thin, bottom=thin)

    align_left_top_wrap = Alignment(horizontal="left", vertical="top", wrap_text=True)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # -------------------------
    # Columns
    # -------------------------
    columns = ["Наименование", "Область", "Товары", "Контакты"]
    ncols = len(columns)

    # -------------------------
    # Title row
    # -------------------------
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(row=1, column=1, value=title_text)
    c.font = title_font
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 32

    # spacer
    ws.row_dimensions[2].height = 6

    # -------------------------
    # Header row
    # -------------------------
    ws.append([])      # row 2
    ws.append(columns) # row 3
    header_row = 3

    for col_idx in range(1, ncols + 1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = border_thin

    ws.row_dimensions[header_row].height = 20

    # Freeze panes + autofilter
    ws.freeze_panes = ws["A4"]
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(ncols)}{header_row}"

    # -------------------------
    # Helpers
    # -------------------------
    def format_contacts(company):
        def sort_primary_first(items):
            # items: iterable with attr is_primary (bool)
            return sorted(items, key=lambda x: (not getattr(x, "is_primary", False), getattr(x, "id", 0)))

        contact_chunks = []

        for c in company.contacts.all():
            name = (c.full_name or "").strip()
            pos = (c.position or "").strip()
            notes = (getattr(c, "notes", "") or "").strip()

            # Заголовок контакта
            if name:
                header = name
                if pos:
                    header = f"{header} - {pos}"
            else:
                # нет ФИО -> вместо ФИО/Должности пишем notes
                # если notes пустой, то хотя бы прочерк, чтобы контакт не был пустым
                header = notes if notes else "-"

            # Телефоны / emails с primary первым
            phones = sort_primary_first(c.phones.all())
            emails = sort_primary_first(c.emails.all())

            phone_str = ", ".join(p.phone for p in phones if getattr(p, "phone", None))
            email_str = "; ".join(e.email for e in emails if getattr(e, "email", None))

            # Сборка строки контакта
            parts = []
            if phone_str:
                parts.append(phone_str)
            if email_str:
                parts.append(email_str)

            if parts:
                contact_chunks.append(f"{header}: " + "; ".join(parts))
            else:
                contact_chunks.append(header)

        return " | ".join(contact_chunks)

    def format_products(company):
        products = company.product.all()
        return ", ".join(p.name for p in products) if products else ""

    # -------------------------
    # Column widths
    # -------------------------
    widths = {1: 42, 2: 26, 3: 40, 4: 60}
    for col_idx, w in widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    # -------------------------
    # Data rows
    # -------------------------
    row_idx = 4
    for company in companies_qs:
        ws.append([
            company.name_ru or "",
            format_kato_region_name(company),  # ✅ теперь название региона по "коду с нулями"
            format_products(company),
            format_contacts(company),
        ])

        for col_idx in range(1, ncols + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.alignment = align_left_top_wrap
            cell.border = border_thin

        ws.row_dimensions[row_idx].height = 48
        row_idx += 1

    return wb

