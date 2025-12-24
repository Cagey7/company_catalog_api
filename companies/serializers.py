from rest_framework import serializers
from .models import *


class CompanyBinSerializer(serializers.Serializer):
    company_bin = serializers.CharField()

    def validate(self, data):
        company_bin = data.get("company_bin")
        if not company_bin.isdigit():
            raise serializers.ValidationError("Некорректный БИН.")
        return data


class CompanySerializer(serializers.Serializer):
    company_bin = serializers.CharField(required=False)
    name_ru = serializers.CharField(required=False)


    def validate(self, data):
        try:
            Company.objects.get(id=data.get("company_bin"))
        except:
            raise serializers.ValidationError("Компании с таким БИНом не существует")

        try:
            Company.objects.get(id=data.get("name_ru"))
        except:
            raise serializers.ValidationError("Компании с таким БИНом не существует")
        return data


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