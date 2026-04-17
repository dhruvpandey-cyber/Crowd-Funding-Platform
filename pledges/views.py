from rest_framework import permissions, viewsets

from .models import Pledge
from .serializers import PledgeSerializer


class PledgeViewSet(viewsets.ModelViewSet):
	serializer_class = PledgeSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ["campaign", "status"]

	def get_queryset(self):
		if self.request.user.is_staff:
			return Pledge.objects.select_related("backer", "campaign", "reward_tier").all()
		return Pledge.objects.select_related("backer", "campaign", "reward_tier").filter(backer=self.request.user)

	def perform_create(self, serializer):
		serializer.save(backer=self.request.user)
