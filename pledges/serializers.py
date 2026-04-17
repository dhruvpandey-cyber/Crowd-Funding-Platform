from django.utils import timezone
from rest_framework import serializers

from .models import Pledge


class PledgeSerializer(serializers.ModelSerializer):
    backer_name = serializers.CharField(source="backer.username", read_only=True)
    campaign_title = serializers.CharField(source="campaign.title", read_only=True)

    class Meta:
        model = Pledge
        fields = [
            "id",
            "backer",
            "backer_name",
            "campaign",
            "campaign_title",
            "reward_tier",
            "amount",
            "status",
            "payment_reference",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["backer", "status", "payment_reference"]

    def validate(self, attrs):
        campaign = attrs["campaign"]
        user = self.context["request"].user
        amount = attrs["amount"]

        if campaign.creator_id == user.id:
            raise serializers.ValidationError("You cannot pledge to your own campaign.")
        if campaign.status != campaign.Status.ACTIVE:
            raise serializers.ValidationError("Only active campaigns can receive pledges.")
        if campaign.deadline <= timezone.now():
            raise serializers.ValidationError("Campaign deadline has passed.")
        if amount < campaign.min_pledge_amount:
            raise serializers.ValidationError("Amount is less than campaign minimum pledge.")
        return attrs