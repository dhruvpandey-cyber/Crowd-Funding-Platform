from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Pledge(models.Model):
	class Status(models.TextChoices):
		INITIATED = "INITIATED", "Initiated"
		AUTHORIZED = "AUTHORIZED", "Authorized"
		CAPTURED = "CAPTURED", "Captured"
		REFUNDED = "REFUNDED", "Refunded"
		CANCELLED = "CANCELLED", "Cancelled"

	backer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pledges")
	campaign = models.ForeignKey("campaigns.Campaign", on_delete=models.CASCADE, related_name="pledges")
	reward_tier = models.ForeignKey(
		"campaigns.RewardTier", on_delete=models.SET_NULL, null=True, blank=True, related_name="pledges"
	)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
	payment_reference = models.CharField(max_length=100, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def clean(self):
		if self.campaign.deadline <= timezone.now():
			raise ValidationError("Campaign is already closed.")
		if self.amount < self.campaign.min_pledge_amount:
			raise ValidationError("Pledge amount is below minimum pledge amount.")
		if self.reward_tier and self.reward_tier.campaign_id != self.campaign_id:
			raise ValidationError("Selected reward tier does not belong to this campaign.")

	def __str__(self):
		return f"{self.backer} -> {self.campaign} ({self.amount})"
