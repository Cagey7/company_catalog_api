from django.core.management.base import BaseCommand
from django.db import transaction

from dictionaries.models import Krp, Kfc, Kse, Oked, Tnved, Kato, Industry, Product
from dictionaries.data.krp import krp_dict
from dictionaries.data.kfc import kfc_dict
from dictionaries.data.kse import kse_dict
from dictionaries.data.oked import oked_dict
from dictionaries.data.tn_ved import tn_ved_dict
from dictionaries.data.kato import kato_dict
from dictionaries.data.industry import industries_tree
from dictionaries.data.product import product_dict


class Command(BaseCommand):
    help = "Загрузка классификаторов (КРП, КФС, КСЕ, ОКЭД, ТН ВЭД, КАТО, Industry, Product)"

    def handle(self, *args, **options):
        self.load_krp()
        self.load_kse()
        self.load_oked()
        self.load_kato()
        self.load_products()
        self.load_kfc()
        self.load_tn_ved()
        self.load_industries()
        self.stdout.write(self.style.SUCCESS("✅ Все классификаторы загружены"))

    def load_kfc(self):
        with transaction.atomic():
            for code, name in kfc_dict.items():
                code = str(code).strip()
                name = str(name).strip()
                obj, created = Kfc.objects.get_or_create(kfc_code=code, defaults={"kfc_name": name})
                if not created and obj.kfc_name != name:
                    obj.kfc_name = name
                    obj.save(update_fields=["kfc_name"])

    def load_tn_ved(self):
        with transaction.atomic():
            for code, name in tn_ved_dict.items():
                code = str(code).strip()
                name = str(name).strip()
                obj, created = Tnved.objects.get_or_create(tn_ved_code=code, defaults={"tn_ved_name": name})
                if not created and obj.tn_ved_name != name:
                    obj.tn_ved_name = name
                    obj.save(update_fields=["tn_ved_name"])

    def load_industries(self):
        with transaction.atomic():
            for item in industries_tree:
                name = item["name"].strip()
                Industry.objects.get_or_create(name=name, parent=None)

    def load_tree(self, data, model, code_field: str, name_field: str):
        has_path = any(f.name == "path" for f in model._meta.get_fields())

        def upsert_node(node, parent=None, parent_path=""):
            code = str(node["code"]).strip()
            name = str(node["name"]).strip()
            children = node.get("children") or []
            current_path = f"{parent_path}{code}/" if has_path else None
            defaults = {name_field: name, "parent": parent}
            if has_path:
                defaults["path"] = current_path
            obj, created = model.objects.get_or_create(**{code_field: code}, defaults=defaults)
            changed_fields = []
            if getattr(obj, name_field) != name:
                setattr(obj, name_field, name)
                changed_fields.append(name_field)
            if obj.parent_id != (parent.id if parent else None):
                obj.parent = parent
                changed_fields.append("parent")
            if has_path and getattr(obj, "path") != current_path:
                obj.path = current_path
                changed_fields.append("path")
            if changed_fields:
                obj.save(update_fields=changed_fields)
            for child in children:
                upsert_node(child, parent=obj, parent_path=current_path if has_path else parent_path)

        with transaction.atomic():
            for root in data:
                upsert_node(root, parent=None, parent_path="")

    def load_krp(self):
        self.load_tree(data=krp_dict, model=Krp, code_field="krp_code", name_field="krp_name")

    def load_kse(self):
        self.load_tree(data=kse_dict, model=Kse, code_field="kse_code", name_field="kse_name")

    def load_oked(self):
        self.load_tree(data=oked_dict, model=Oked, code_field="oked_code", name_field="oked_name")

    def load_kato(self):
        self.load_tree(data=kato_dict, model=Kato, code_field="kato_code", name_field="kato_name")

    def load_products(self):
        def upsert_product(node, parent=None, parent_path=""):
            name = str(node["name"]).strip()
            children = node.get("children") or []
            current_path = f"{parent_path}{name}/"
            obj, created = Product.objects.get_or_create(name=name, defaults={"parent": parent, "path": current_path})
            changed_fields = []
            if obj.parent_id != (parent.id if parent else None):
                obj.parent = parent
                changed_fields.append("parent")
            if getattr(obj, "path", None) != current_path:
                obj.path = current_path
                changed_fields.append("path")
            if changed_fields:
                obj.save(update_fields=changed_fields)
            for child in children:
                upsert_product(child, parent=obj, parent_path=current_path)

        with transaction.atomic():
            for root in product_dict:
                upsert_product(root, parent=None, parent_path="")
