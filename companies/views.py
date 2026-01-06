import requests
import time
from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .serializers import *
from .models import *
from metrics.models import *
from dictionaries.models import *

from .services.prg_loader import load_company_data_by_bin, CompanyLoadError


class LoadCompanyData(APIView):
    def post(self, request):
        serializer = CompanyBinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_bin = serializer.validated_data["company_bin"]

        try:
            result = load_company_data_by_bin(company_bin)
            return Response(result, status=status.HTTP_200_OK)
        except CompanyLoadError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class GetCompanyData(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name_ru", "name_kz", "company_bin"]

    def get_queryset(self):
        return Company.objects.all()


class CompanyDetailAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    lookup_field = "company_bin"

    def get_queryset(self):
        return (
            Company.objects
            .select_related("krp", "kse", "kfc", "kato", "industry", "primary_oked")
            .prefetch_related(
                "product",
                "secondary_okeds",
                "taxes",
                "nds",
                "goszakupsupplier",
                "goszakupcustomer",
                "program_participations__program",
                "contacts__emails",
                "contacts__phones",
            )
        )
