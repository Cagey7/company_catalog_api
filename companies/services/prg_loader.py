import requests
from datetime import datetime
from django.db import transaction

from companies.models import Company
from metrics.models import Taxes, Nds, GosZakupSupplier, GosZakupCustomer
from dictionaries.models import Krp, Kse, Kfc, Kato, Oked


class CompanyLoadError(Exception):
    pass


def load_company_data_by_bin(company_bin: str) -> dict:
    company_url = "https://apiba.prgapp.kz/CompanyFullInfo"
    goz_zakup_url = "https://apiba.prgapp.kz/CompanyGosZakupGraph"

    company_params = {"id": company_bin, "lang": "ru"}
    goz_zakup_params = {"bin": company_bin, "lang": "ru"}

    company_response = requests.get(company_url, params=company_params, timeout=30)
    gos_zakup_response = requests.get(goz_zakup_url, params=goz_zakup_params, timeout=30)

    if not (company_response.status_code == 200 and gos_zakup_response.status_code == 200):
        raise CompanyLoadError(
            f"PRGAPP failed. company={company_response.status_code}, gos_zakup={gos_zakup_response.status_code}"
        )

    c_data = company_response.json()
    g_data = gos_zakup_response.json()

    if c_data.get("basicInfo", {}).get("isDeleted"):
        return {"status": "deleted", "message": f"Компания удалена. БИН: {company_bin}"}

    def g(path, default=None):
        cur = c_data
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                return default
            cur = cur[key]
        return cur if cur is not None else default

    name_ru = g(["basicInfo", "titleRu", "value"])
    name_kz = g(["basicInfo", "titleKz", "value"])

    reg_raw = g(["basicInfo", "registrationDate", "value"])
    try:
        register_date = datetime.fromisoformat(reg_raw).date() if reg_raw else None
    except Exception:
        register_date = None

    ceo = g(["basicInfo", "ceo", "value", "title"])
    pay_nds = g(["basicInfo", "isNds", "value"])
    tax_risk = g(["basicInfo", "degreeOfRisk", "value"])
    address = g(["basicInfo", "address", "value"])

    api_bin = g(["basicInfo", "bin"])
    if not api_bin:
        raise CompanyLoadError("БИН не найден в ответе PRGAPP.")
    company_bin = api_bin

    phone_number = None
    try:
        phone_number = c_data["gosZakupContacts"]["phone"][0]["value"]
    except Exception:
        try:
            phone_number = c_data["egovContacts"]["phone"][0]["value"]
        except Exception:
            phone_number = None

    email = None
    try:
        email = c_data["gosZakupContacts"]["email"][0]["value"]
    except Exception:
        email = None

    krp_code = g(["basicInfo", "krp", "value", "value"])
    krp_name = g(["basicInfo", "krp", "value", "description"])
    kse_code = g(["basicInfo", "kse", "value", "value"])
    kse_name = g(["basicInfo", "kse", "value", "description"])
    kfc_code = g(["basicInfo", "kfc", "value", "value"])
    kfc_name = g(["basicInfo", "kfc", "value", "description"])
    kato_code = g(["basicInfo", "kato", "value", "value"])
    kato_name = g(["basicInfo", "kato", "value", "description"])

    primary_oked = g(["basicInfo", "primaryOKED", "value"])
    secondary_okeds = g(["basicInfo", "secondaryOKED", "value"], default=None)

    taxes = c_data.get("taxes", {}).get("taxGraph", []) or []
    nds_info = c_data.get("taxes", {}).get("ndsGraph", []) or []
    gos_zakup_as_supplier_info = g_data.get("asSupplier", []) or []
    gos_zakup_as_customer_info = g_data.get("asCustomer", []) or []

    with transaction.atomic():
        krp = Krp.objects.get_or_create(krp_code=krp_code, defaults={"krp_name": krp_name})[0] if krp_code else None
        kse = Kse.objects.get_or_create(kse_code=kse_code, defaults={"kse_name": kse_name})[0] if kse_code else None
        kfc = Kfc.objects.get_or_create(kfc_code=kfc_code, defaults={"kfc_name": kfc_name})[0] if kfc_code else None
        kato = Kato.objects.get_or_create(kato_code=kato_code, defaults={"kato_name": kato_name})[0] if kato_code else None

        oked_obj = None
        if primary_oked:
            try:
                oked_code, oked_name = primary_oked.split(" ", 1)
                oked_obj = Oked.objects.get_or_create(oked_code=oked_code, defaults={"oked_name": oked_name})[0]
            except Exception:
                oked_obj = None

        company, created = Company.objects.get_or_create(
            company_bin=company_bin,
            defaults={
                "name_ru": name_ru,
                "name_kz": name_kz,
                "register_date": register_date,
                "ceo": ceo,
                "pay_nds": pay_nds,
                "tax_risk": tax_risk,
                "address": address,
                "phone_number": phone_number,
                "email": email,
                "krp": krp,
                "kse": kse,
                "kfc": kfc,
                "kato": kato,
                "primary_oked": oked_obj,
            },
        )

        if not created:
            company.name_ru = name_ru
            company.name_kz = name_kz
            company.register_date = register_date
            company.ceo = ceo
            company.pay_nds = pay_nds
            company.tax_risk = tax_risk
            company.address = address
            company.phone_number = phone_number
            company.email = email
            company.krp = krp
            company.kse = kse
            company.kfc = kfc
            company.kato = kato
            company.primary_oked = oked_obj
            company.save()

        if secondary_okeds:
            company.secondary_okeds.clear()
            for oked_info in secondary_okeds:
                try:
                    oked_code, oked_name = oked_info.strip().split(maxsplit=1)
                except ValueError:
                    oked_code, oked_name = oked_info.strip(), oked_info.strip()
                oked2 = Oked.objects.get_or_create(oked_code=oked_code, defaults={"oked_name": oked_name})[0]
                company.secondary_okeds.add(oked2)

        def latest_year(qs):
            v = qs.values_list("year", flat=True)
            return max(v) if v else 0

        lt = latest_year(Taxes.objects.filter(company=company))
        for t in taxes:
            if t["year"] > lt:
                Taxes.objects.create(company=company, year=t["year"], value=t["value"])

        ln = latest_year(Nds.objects.filter(company=company))
        for n in nds_info:
            if n["year"] > ln:
                Nds.objects.create(company=company, year=n["year"], value=n["value"])

        lgs = latest_year(GosZakupSupplier.objects.filter(company=company))
        for s in gos_zakup_as_supplier_info:
            if s["year"] > lgs:
                GosZakupSupplier.objects.create(company=company, year=s["year"], value=s["value"])

        lgc = latest_year(GosZakupCustomer.objects.filter(company=company))
        for c in gos_zakup_as_customer_info:
            if c["year"] > lgc:
                GosZakupCustomer.objects.create(company=company, year=c["year"], value=c["value"])

    return {
        "status": "created" if created else "updated",
        "message": ("Данные компании загружены." if created else "Данные компании обновлены."),
        "company_bin": company_bin,
        "company_id": company.id,
    }
