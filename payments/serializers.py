from rest_framework import serializers

from .models import Payment, PayoutRequest, Refund


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "pledge", "gateway", "transaction_id", "amount", "status", "paid_at", "created_at"]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ["id", "payment", "amount", "reason", "status", "created_at"]


class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = [
            "id",
            "creator",
            "campaign",
            "requested_amount",
            "status",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["creator", "status"]