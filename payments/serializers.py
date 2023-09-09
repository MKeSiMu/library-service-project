import datetime

from rest_framework import serializers

from borrowings.serializers import BorrowingDetailSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    money_to_pay = serializers.FloatField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentDetailSerializer(PaymentSerializer):
    borrowing_id = BorrowingDetailSerializer(read_only=True)
