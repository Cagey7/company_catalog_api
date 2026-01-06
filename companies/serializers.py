from rest_framework import serializers
from .models import Company, CompanyContact, ContactEmail, ContactPhone
from programs.serializers import ProgramParticipationReadSerializer
from metrics.serializers import (
    TaxesSerializer,
    NdsSerializer,
    GosZakupSupplierSerializer,
    GosZakupCustomerSerializer,
)


class CompanyBinSerializer(serializers.Serializer):
    company_bin = serializers.CharField()

    def validate(self, data):
        company_bin = data.get("company_bin")
        if not company_bin.isdigit():
            raise serializers.ValidationError("Некорректный БИН.")
        return data


class ContactEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEmail
        fields = ["id", "email", "is_primary", "is_mailing"]


class ContactPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPhone
        fields = ["id", "phone", "is_primary", "is_mailing"]


class CompanyContactSerializer(serializers.ModelSerializer):
    emails = ContactEmailSerializer(many=True, read_only=True)
    phones = ContactPhoneSerializer(many=True, read_only=True)

    class Meta:
        model = CompanyContact
        fields = ["id", "full_name", "position", "notes", "emails", "phones"]


class CompanySerializer(serializers.ModelSerializer):
    # контакты
    contacts = CompanyContactSerializer(many=True, read_only=True)

    # метрики
    taxes = TaxesSerializer(many=True, read_only=True)
    nds = NdsSerializer(many=True, read_only=True)
    goszakupsupplier = GosZakupSupplierSerializer(many=True, read_only=True)
    goszakupcustomer = GosZakupCustomerSerializer(many=True, read_only=True)

    # программы
    program_participations = ProgramParticipationReadSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = "__all__"
