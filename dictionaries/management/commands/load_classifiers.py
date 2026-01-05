from django.core.management.base import BaseCommand
from django.db import transaction

from dictionaries.models import Krp, Kfc, Kse, Oked, Tnved, Kato, Industry

from dictionaries.data.krp import krp_dict
from dictionaries.data.kfc import kfc_dict
from dictionaries.data.kse import kse_dict
from dictionaries.data.oked import oked_dict
from dictionaries.data.tn_ved import tn_ved_dict
from dictionaries.data.kato import kato_dict
from dictionaries.data.industry import industries_tree


class Command(BaseCommand):
    help = "Загрузка классификаторов (КРП, КФС, КСЕ, ОКЭД, ТН ВЭД, КАТО, Industry)"

    def handle(self, *args, **options):
        self.load_krp()
        self.load_kfc()

        # ✅ деревья
        self.load_kse()
        self.load_oked()
        self.load_kato()

        self.load_tn_ved()
        self.load_industries()

        self.stdout.write(self.style.SUCCESS("✅ Все классификаторы загружены"))

    # ---------- плоские справочники ----------

    def load_krp(self):
        for code, name in krp_dict.items():
            Krp.objects.get_or_create(
                krp_code=str(code).strip(),
                defaults={"krp_name": str(name).strip()},
            )

    def load_kfc(self):
        for code, name in kfc_dict.items():
            Kfc.objects.get_or_create(
                kfc_code=str(code).strip(),
                defaults={"kfc_name": str(name).strip()},
            )

    def load_tn_ved(self):
        for code, name in tn_ved_dict.items():
            Tnved.objects.get_or_create(
                tn_ved_code=str(code).strip(),
                defaults={"tn_ved_name": str(name).strip()},
            )

    def load_industries(self):
        for item in industries_tree:
            Industry.objects.get_or_create(
                name=item["name"].strip(),
                parent=None
            )

    # ---------- универсальный загрузчик деревьев ----------

    def load_tree(self, data, model, code_field: str, name_field: str):
        """
        data: list[dict] формата {"code": "...", "name": "...", "children": [...]}
        model: Kse / Oked / Kato
        code_field: "kse_code" / "oked_code" / "kato_code"
        name_field: "kse_name" / "oked_name" / "kato_name"

        Обновляет name и parent при повторных запусках.
        """

        def upsert_node(node, parent=None):
            code = str(node["code"]).strip()
            name = str(node["name"]).strip()
            children = node.get("children") or []

            obj, created = model.objects.get_or_create(
                **{code_field: code},
                defaults={name_field: name, "parent": parent},
            )

            # ✅ синхронизация при повторных запусках
            changed = False
            if getattr(obj, name_field) != name:
                setattr(obj, name_field, name)
                changed = True

            if obj.parent_id != (parent.id if parent else None):
                obj.parent = parent
                changed = True

            if changed:
                obj.save(update_fields=[name_field, "parent"])

            for child in children:
                upsert_node(child, parent=obj)

        with transaction.atomic():
            for root in data:
                upsert_node(root, parent=None)

    # ---------- деревья: KSE / OKED / KATO ----------

    def load_kse(self):
        self.load_tree(
            data=kse_dict,
            model=Kse,
            code_field="kse_code",
            name_field="kse_name",
        )

    def load_oked(self):
        self.load_tree(
            data=oked_dict,
            model=Oked,
            code_field="oked_code",
            name_field="oked_name",
        )

    def load_kato(self):
        self.load_tree(
            data=kato_dict,
            model=Kato,
            code_field="kato_code",
            name_field="kato_name",
        )
