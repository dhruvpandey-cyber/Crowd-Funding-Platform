from rest_framework import serializers

from .models import Campaign, CampaignComment, CampaignMedia, CampaignUpdate, Category, FavoriteCampaign, RewardTier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class RewardTierSerializer(serializers.ModelSerializer):
    claimed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RewardTier
        fields = [
            "id",
            "campaign",
            "title",
            "description",
            "amount",
            "quantity",
            "estimated_delivery",
            "claimed_count",
        ]


class CampaignMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignMedia
        fields = ["id", "campaign", "media_type", "file", "external_url", "created_at"]


class CampaignListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    total_raised = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_percent = serializers.FloatField(read_only=True)
    hero_media_url = serializers.SerializerMethodField()

    def get_hero_media_url(self, obj):
        media = obj.media.filter(media_type=CampaignMedia.MediaType.IMAGE).order_by("id").first()
        if not media:
            return ""
        if media.file:
            request = self.context.get("request")
            url = media.file.url
            return request.build_absolute_uri(url) if request else url
        return media.external_url

    class Meta:
        model = Campaign
        fields = [
            "id",
            "title",
            "short_description",
            "goal_amount",
            "deadline",
            "status",
            "is_featured",
            "creator_name",
            "category_name",
            "total_raised",
            "progress_percent",
            "hero_media_url",
            "created_at",
        ]


class CampaignDetailSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    total_raised = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_percent = serializers.FloatField(read_only=True)
    reward_tiers = RewardTierSerializer(many=True, read_only=True)
    media = CampaignMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "creator",
            "creator_name",
            "category",
            "category_name",
            "title",
            "short_description",
            "story",
            "goal_amount",
            "min_pledge_amount",
            "deadline",
            "status",
            "is_featured",
            "total_raised",
            "progress_percent",
            "reward_tiers",
            "media",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["creator", "status"]


class CampaignUpdateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = CampaignUpdate
        fields = ["id", "campaign", "title", "content", "created_by", "created_by_name", "created_at"]
        read_only_fields = ["created_by"]


class CampaignCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = CampaignComment
        fields = ["id", "campaign", "user", "user_name", "comment", "created_at"]
        read_only_fields = ["user"]


class FavoriteCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteCampaign
        fields = ["id", "user", "campaign", "created_at"]
        read_only_fields = ["user"]