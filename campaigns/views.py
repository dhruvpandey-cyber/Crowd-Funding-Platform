from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Campaign, CampaignComment, CampaignMedia, CampaignUpdate, Category, FavoriteCampaign, RewardTier
from .permissions import IsCreatorOrReadOnly
from .serializers import (
	CampaignCommentSerializer,
	CampaignDetailSerializer,
	CampaignListSerializer,
	CampaignMediaSerializer,
	CampaignUpdateSerializer,
	CategorySerializer,
	RewardTierSerializer,
)
from pledges.models import Pledge


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CampaignViewSet(viewsets.ModelViewSet):
	queryset = Campaign.objects.select_related("creator", "category").all()
	permission_classes = [IsCreatorOrReadOnly]
	filterset_fields = ["status", "category", "is_featured"]
	search_fields = ["title", "short_description", "story"]
	ordering_fields = ["created_at", "deadline", "goal_amount"]

	def get_serializer_class(self):
		if self.action in ["list", "mine"]:
			return CampaignListSerializer
		return CampaignDetailSerializer

	def perform_create(self, serializer):
		serializer.save(creator=self.request.user)

	@action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
	def mine(self, request):
		queryset = self.get_queryset().filter(creator=request.user)
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	@action(
		detail=False,
		methods=["get"],
		permission_classes=[permissions.IsAuthenticated],
		url_path="creator-stats",
	)
	def creator_stats(self, request):
		campaigns = self.get_queryset().filter(creator=request.user)
		campaign_ids = list(campaigns.values_list("id", flat=True))

		received_qs = Pledge.objects.filter(campaign_id__in=campaign_ids, status__in=["AUTHORIZED", "CAPTURED"])
		intent_qs = Pledge.objects.filter(campaign_id__in=campaign_ids).exclude(status="CANCELLED")

		received_total = sum((p.amount for p in received_qs), 0)
		pledged_total = sum((p.amount for p in intent_qs), 0)

		recent_pledges = (
			Pledge.objects.select_related("backer", "campaign")
			.filter(campaign_id__in=campaign_ids)
			.order_by("-created_at")[:10]
		)

		return Response(
			{
				"campaign_count": len(campaign_ids),
				"received_total": str(received_total),
				"pledged_total": str(pledged_total),
				"received_pledges_count": received_qs.count(),
				"all_pledges_count": intent_qs.count(),
				"recent_pledges": [
					{
						"id": pledge.id,
						"campaign_id": pledge.campaign_id,
						"campaign_title": pledge.campaign.title,
						"backer_name": pledge.backer.username,
						"amount": str(pledge.amount),
						"status": pledge.status,
						"created_at": pledge.created_at,
					}
					for pledge in recent_pledges
				],
			}
		)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def set_status(self, request, pk=None):
		campaign = self.get_object()
		new_status = request.data.get("status")
		allowed = {
			Campaign.Status.DRAFT,
			Campaign.Status.PENDING_REVIEW,
			Campaign.Status.ACTIVE,
			Campaign.Status.CANCELLED,
		}

		if new_status not in allowed:
			return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

		if not (request.user.is_staff or campaign.creator_id == request.user.id):
			return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

		campaign.status = new_status
		campaign.save(update_fields=["status", "updated_at"])
		return Response({"detail": "Campaign status updated.", "status": campaign.status})

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def favorite(self, request, pk=None):
		campaign = self.get_object()
		_, created = FavoriteCampaign.objects.get_or_create(user=request.user, campaign=campaign)
		if not created:
			return Response({"detail": "Campaign already in favorites."}, status=status.HTTP_200_OK)
		return Response({"detail": "Campaign added to favorites."}, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
	def unfavorite(self, request, pk=None):
		campaign = self.get_object()
		FavoriteCampaign.objects.filter(user=request.user, campaign=campaign).delete()
		return Response({"detail": "Campaign removed from favorites."}, status=status.HTTP_200_OK)


class RewardTierViewSet(viewsets.ModelViewSet):
	queryset = RewardTier.objects.select_related("campaign").all()
	serializer_class = RewardTierSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	filterset_fields = ["campaign"]


class CampaignUpdateViewSet(viewsets.ModelViewSet):
	queryset = CampaignUpdate.objects.select_related("campaign", "created_by").all()
	serializer_class = CampaignUpdateSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	filterset_fields = ["campaign"]

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)


class CampaignCommentViewSet(viewsets.ModelViewSet):
	queryset = CampaignComment.objects.select_related("campaign", "user").all()
	serializer_class = CampaignCommentSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	filterset_fields = ["campaign"]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class CampaignMediaViewSet(viewsets.ModelViewSet):
	queryset = CampaignMedia.objects.select_related("campaign").all()
	serializer_class = CampaignMediaSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	filterset_fields = ["campaign", "media_type"]

	def perform_create(self, serializer):
		campaign = serializer.validated_data["campaign"]
		if not (self.request.user.is_staff or campaign.creator_id == self.request.user.id):
			raise PermissionDenied("Only campaign owner can upload media.")
		serializer.save()
