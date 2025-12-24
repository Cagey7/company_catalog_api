from rest_framework import serializers
from .models import *
from companies.models import *


class KrpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Krp
        exclude = ["id"]


class KseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kse
        exclude = ["id"]


class KfcSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kfc
        exclude = ["id"]


class KatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kato
        exclude = ["id"]


class OkedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oked
        exclude = ["id"]



class CompanySerializer(serializers.ModelSerializer):
    krp = KrpSerializer()
    kse = KseSerializer()
    kfc = KfcSerializer()
    kato = KatoSerializer()
    primary_oked = OkedSerializer()
    secondary_okeds = OkedSerializer(many=True)


    class Meta:
        model = Company
        exclude = ["id"]