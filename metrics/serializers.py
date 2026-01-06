from rest_framework import serializers
from .models import *

class TaxesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxes
        fields = ["year", "value"]

class NdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nds
        fields = ["year", "value"]
 
class GosZakupSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = GosZakupSupplier
        fields = ["year", "value"]

class GosZakupCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GosZakupCustomer
        fields = ["year", "value"]
