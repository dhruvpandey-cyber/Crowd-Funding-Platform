from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import AuditLog, Report
from .serializers import AuditLogSerializer, ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
	serializer_class = ReportSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ["campaign", "status"]

	def get_queryset(self):
		if self.request.user.is_staff:
			return Report.objects.select_related("reporter", "campaign").all()
		return Report.objects.select_related("reporter", "campaign").filter(reporter=self.request.user)

	def perform_create(self, serializer):
		serializer.save(reporter=self.request.user, status=Report.Status.OPEN)

	def perform_update(self, serializer):
		if not self.request.user.is_staff:
			raise PermissionDenied("Only admins can update reports.")
		instance = serializer.save()
		if instance.status in [instance.Status.RESOLVED, instance.Status.REJECTED] and not instance.resolved_at:
			instance.resolved_at = timezone.now()
			instance.save(update_fields=["resolved_at"])

	def perform_destroy(self, instance):
		if not self.request.user.is_staff:
			raise PermissionDenied("Only admins can delete reports.")
		instance.delete()


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = AuditLog.objects.select_related("actor").all()
