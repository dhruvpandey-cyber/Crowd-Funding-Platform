from django.conf import settings
from django.db import models


class Payment(models.Model):
	class Status(models.TextChoices):
		PENDING = "PENDING", "Pending"
		SUCCESS = "SUCCESS", "Success"
		FAILED = "FAILED", "Failed"

	pledge = models.OneToOneField("pledges.Pledge", on_delete=models.CASCADE, related_name="payment")
	gateway = models.CharField(max_length=50, default="sandbox")
	transaction_id = models.CharField(max_length=120, unique=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	paid_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.transaction_id} ({self.status})"


class Refund(models.Model):
	class Status(models.TextChoices):
		INITIATED = "INITIATED", "Initiated"
		PROCESSED = "PROCESSED", "Processed"
		FAILED = "FAILED", "Failed"

	payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="refunds")
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	reason = models.CharField(max_length=255)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
	created_at = models.DateTimeField(auto_now_add=True)


class PayoutRequest(models.Model):
	class Status(models.TextChoices):
		PENDING = "PENDING", "Pending"
		APPROVED = "APPROVED", "Approved"
		REJECTED = "REJECTED", "Rejected"
		PAID = "PAID", "Paid"

	creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payout_requests")
	campaign = models.ForeignKey("campaigns.Campaign", on_delete=models.CASCADE, related_name="payout_requests")
	requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	note = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
