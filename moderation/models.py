from django.conf import settings
from django.db import models


class Report(models.Model):
	class Status(models.TextChoices):
		OPEN = "OPEN", "Open"
		UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
		RESOLVED = "RESOLVED", "Resolved"
		REJECTED = "REJECTED", "Rejected"

	reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_made")
	campaign = models.ForeignKey("campaigns.Campaign", on_delete=models.CASCADE, related_name="reports")
	reason = models.CharField(max_length=255)
	details = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
	created_at = models.DateTimeField(auto_now_add=True)
	resolved_at = models.DateTimeField(null=True, blank=True)


class AuditLog(models.Model):
	actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	action = models.CharField(max_length=150)
	target_model = models.CharField(max_length=80)
	target_id = models.CharField(max_length=80)
	metadata = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
