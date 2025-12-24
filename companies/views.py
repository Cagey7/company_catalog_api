import requests
import time
from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .serializers import *
from .models import *
from dictionaries.models import *


class LoadCompanyData(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = CompanyBinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_bin = serializer.data["company_bin"]
        
        company_url = "https://apiba.prgapp.kz/CompanyFullInfo"
        
        company_params = {
            "id": {company_bin},
            "lang": "ru"
        }
        
        goz_zakup_params = {
            "bin": {company_bin},
            "lang": "ru"
        }
        
        company_response = requests.get(company_url, params=company_params)

        if company_response.status_code == 200:
            c_data = company_response.json()
            
            is_deleted = c_data["basicInfo"]["isDeleted"]
            if is_deleted:
                return Response({"message": f"Компания удалена. БИН: {company_bin}"}, status=status.HTTP_200_OK)
            
            try:
                name_ru = c_data["basicInfo"]["titleRu"]["value"]
            except:
                name_ru = None
            
            try:
                name_kz = c_data["basicInfo"]["titleKz"]["value"]
            except:
                name_kz = None
            
            try:
                register_date = datetime.fromisoformat(c_data["basicInfo"]["registrationDate"]["value"]).date()
            except:
                register_date = None
            
            try:
                ceo = c_data["basicInfo"]["ceo"]["value"]["title"]
            except:
                ceo = None
            
            try:
                company_bin = c_data["basicInfo"]["bin"]
            except:
                return Response({"error": "БИН не найден."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                pay_nds = c_data["basicInfo"]["isNds"]["value"]
            except:
                pay_nds = None
            
            try:
                tax_risk = c_data["basicInfo"]["degreeOfRisk"]["value"]
            except:
                tax_risk = None
            
            try:
                address = c_data["basicInfo"]["addressRu"]["value"]
            except:
                address = None
            
            try:
                phone_number = c_data["gosZakupContacts"]["phone"][0]["value"]
            except:
                try:
                    phone_number = c_data["egovContacts"]["phone"][0]["value"]
                except:
                    phone_number = None
            
            try:
                email = c_data["gosZakupContacts"]["email"][0]["value"]
            except:
                email = None
            
            try:
                krp_code = c_data["basicInfo"]["krp"]["value"]["value"]
                krp_name = c_data["basicInfo"]["krp"]["value"]["description"]
            except:
                krp_code = None
                krp = None
            
            try:
                kse_code = c_data["basicInfo"]["kse"]["value"]["value"]
                kse_name = c_data["basicInfo"]["kse"]["value"]["description"]
            except:
                kse_code = None
                kse = None

            
            try:
                kfc_code = c_data["basicInfo"]["kfc"]["value"]["value"]
                kfc_name = c_data["basicInfo"]["kfc"]["value"]["description"]
            except:
                kfc_code = None
                kfc = None
            
            
            try:
                kato_code = c_data["basicInfo"]["kato"]["value"]["value"]
                kato_name = c_data["basicInfo"]["kato"]["value"]["description"]
            except:
                kato_code = None
                kato = None
            
            
            try:
                primary_oked = c_data["basicInfo"]["primaryOKED"]["value"]
            except:
                primary_oked = None
            
            
            try:
                secondary_okeds = c_data["basicInfo"]["secondaryOKED"]["value"]
            except:
                secondary_okeds = None

            try:
                company = Company.objects.get(company_bin=company_bin)
                if krp_code:
                    krp, krp_created = Krp.objects.get_or_create(krp_code=krp_code, defaults={'krp_name': krp_name})
                if kse_code:
                    kse, kse_created = Kse.objects.get_or_create(kse_code=kse_code, defaults={'kse_name': kse_name})
                if kfc_code:
                    kfc, kfc_created = Kfc.objects.get_or_create(kfc_code=kfc_code, defaults={'kfc_name': kfc_name})
                if kato_code:
                    kato, kato_created = Kato.objects.get_or_create(kato_code=kato_code, defaults={'kato_name': kato_name})
                
                if primary_oked:
                    try:
                        oked_code, oked_name = primary_oked.split(" ", 1)
                        oked_obj, oked_created = Oked.objects.get_or_create(oked_code=oked_code, defaults={'oked_name': oked_name})
                    except:
                        oked_obj = None
                
                update_data = {
                    "name_ru": name_ru,
                    "name_kz": name_kz,
                    "register_date": register_date,
                    "ceo": ceo,
                    "pay_nds": pay_nds,
                    "tax_risk": tax_risk,
                    "address_ru": address,
                    "phone_number": phone_number,
                    "email": email,
                    "krp": krp,
                    "kse": kse,
                    "kfc": kfc,
                    "kato": kato,
                    "primary_oked": oked_obj
                }
                
                filtered_update_data = {key: value for key, value in update_data.items() if value is not None}
                company.name_kz = name_kz
                company.name_ru = name_ru
                company.register_date = register_date
                company.ceo = ceo
                company.address = address
                company.phone_number = phone_number
                company.email = email
                company.krp = krp
                company.kse = kse
                company.kato = kato
                company.primary_oked = oked_obj                
                
                if secondary_okeds:
                    old_secondary_okeds = list(company.secondary_okeds.values_list('oked_code', flat=True))
                    new_secondary_okeds = []
                    for oked_info in secondary_okeds:
                        try:
                            oked_code, oked_name = oked_info.split(" ", 1)
                        except:
                            continue
                        try:
                            new_secondary_okeds.append(int(oked_code))
                        except:
                            pass
                    
                    if old_secondary_okeds != new_secondary_okeds:
                        for oked_obj in list(company.secondary_okeds.all()):
                            company.secondary_okeds.remove(oked_obj)
                        for oked_info in secondary_okeds:
                            try:
                                oked_code, oked_name = oked_info.split(" ", 1)
                                oked_obj, _ = Oked.objects.get_or_create(oked_code=oked_code, defaults={'oked_name': oked_name})
                                company.secondary_okeds.add(oked_obj)
                            except:
                                pass
                
                company.save()
                
                return Response({"message": f"Данные компании изменились. БИН: {company_bin}"}, status=status.HTTP_200_OK)
            except:
                with transaction.atomic():
                    if krp_code:
                        krp, krp_created = Krp.objects.get_or_create(krp_code=krp_code, defaults={'krp_name': krp_name})
                    if kse_code:
                        kse, kse_created = Kse.objects.get_or_create(kse_code=kse_code, defaults={'kse_name': kse_name})
                    if kfc_code:
                        kfc, kfc_created = Kfc.objects.get_or_create(kfc_code=kfc_code, defaults={'kfc_name': kfc_name})
                    if kato_code:
                        kato, kato_created = Kato.objects.get_or_create(kato_code=kato_code, defaults={'kato_name': kato_name})
                    
                    if primary_oked:
                        try:
                            oked_code, oked_name = primary_oked.split(" ", 1)
                            oked_obj, oked_created = Oked.objects.get_or_create(oked_code=oked_code, defaults={'oked_name': oked_name})
                        except:
                            oked_obj = None
                        

                    company = Company(name_ru=name_ru,
                                    name_kz=name_kz,
                                    register_date=register_date,
                                    ceo=ceo,
                                    company_bin=company_bin,
                                    address=address,
                                    phone_number=phone_number,
                                    email=email,
                                    krp=krp,
                                    kse=kse,
                                    kfc=kfc,
                                    kato=kato,
                                    primary_oked=oked_obj)
                    
                    company.save()
                    if secondary_okeds:
                        for oked_info in secondary_okeds:
                            try:
                                oked_code, oked_name = oked_info.split(" ", 1)
                                oked_obj, _ = Oked.objects.get_or_create(oked_code=oked_code, defaults={'oked_name': oked_name})
                                company.secondary_okeds.add(oked_obj)
                            except:
                                pass
            
        else:
            return Response({"error": "PRGAPP failed", "company_bin": company_bin, 
                             "company_error_code": company_response.status_code}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"message": f"Данные компании загружены. БИН: {company_bin}"}, status=status.HTTP_200_OK)


    
class GetCompanyData(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name_ru", "name_kz", "company_bin"]
