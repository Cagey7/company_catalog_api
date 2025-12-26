from django.core.management.base import BaseCommand
from dictionaries.models import Krp, Kfc, Kse, Oked, Tnved, Kato, Industry

from dictionaries.data.krp import krp_dict
from dictionaries.data.kfc import kfc_dict
from dictionaries.data.kse import kse_dict
from dictionaries.data.oked import oked_dict
from dictionaries.data.tn_ved import tn_ved_dict
from dictionaries.data.kato import kato_dict
from dictionaries.data.industry import industries_tree


class Command(BaseCommand):
    help = "Загрузка классификаторов (КРП, КФС, КСЕ, ОКЭД)"

    def handle(self, *args, **options):
        self.load_krp()
        self.load_kfc()
        self.load_kse()
        self.load_oked()
        self.load_tn_ved()
        self.load_kato()
        self.load_industries() 

        self.stdout.write(self.style.SUCCESS("✅ Все классификаторы загружены"))

    def load_krp(self):
        for code, name in krp_dict.items():
            Krp.objects.get_or_create(
                krp_code=code,
                defaults={"krp_name": name},
            )

    def load_kfc(self):
        for code, name in kfc_dict.items():
            Kfc.objects.get_or_create(
                kfc_code=code,
                defaults={"kfc_name": name},
            )

    def load_kse(self):
        for code, name in kse_dict.items():
            Kse.objects.get_or_create(
                kse_code=code,
                defaults={"kse_name": name},
            )

    def load_oked(self):
        for code, name in oked_dict.items():
            Oked.objects.get_or_create(
                oked_code=code,
                defaults={"oked_name": name},
            )

    def load_tn_ved(self):
        for code, name in tn_ved_dict.items():
            Tnved.objects.get_or_create(
                tn_ved_code=code,
                defaults={"tn_ved_name": name},
            )


    def load_kato(self):
        for code, name in kato_dict.items():
            Kato.objects.get_or_create(
                kato_code=code,
                defaults={"kato_name": name},
            )


    def load_industries(self):
        for item in industries_tree:
            Industry.objects.get_or_create(
                name=item["name"].strip(),
                parent=None
            )