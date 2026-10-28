from rest_framework import serializers
from .models import SellerBankDetails
import requests

class SellerBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerBankDetails
        fields = '__all__'
        read_only_fields = ('bank_name', 'bank_branch', 'bank_code', 'status', 'verified')

    def validate_ifsc_code(self, value):
        """Validate IFSC and fetch bank details."""
        if len(value) != 11:
            raise serializers.ValidationError("IFSC code must be 11 characters.")
        return value

    def create(self, validated_data):
        # Fetch IFSC details
        ifsc = validated_data['ifsc_code']
        bank_data = get_bank_details_from_ifsc(ifsc)
        if bank_data:
            validated_data['bank_name'] = bank_data.get('BANK')
            validated_data['bank_branch'] = bank_data.get('BRANCH')
            validated_data['bank_code'] = bank_data.get('BANKCODE')
            validated_data['status'] = 'verified'
            validated_data['verified'] = True
        else:
            validated_data['status'] = 'rejected'
            validated_data['verified'] = False

        return super().create(validated_data)


def get_bank_details_from_ifsc(ifsc_code):
    """
    Use a free IFSC API to fetch bank details.
    Example: https://ifsc.razorpay.com/<IFSC>
    """
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'BANK': data.get('BANK'),
                'BRANCH': data.get('BRANCH'),
                'BANKCODE': data.get('BANKCODE')
            }
    except Exception as e:
        print("IFSC lookup failed:", e)
    return None
