from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["transaction_signature","transfer_identifier", "account_number","user_name","transfer_amount", "is_finish"]