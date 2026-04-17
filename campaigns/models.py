from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name


class Campaign(models.Model):
	class Status(models.TextChoices):
		DRAFT = "DRAFT", "Draft"
		PENDING_REVIEW = "PENDING_REVIEW", "Pending Review"
		ACTIVE = "ACTIVE", "Active"
		SUCCESSFUL = "SUCCESSFUL", "Successful"
		FAILED = "FAILED", "Failed"
		CANCELLED = "CANCELLED", "Cancelled"

	creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns")
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="campaigns")
	title = models.CharField(max_length=255)
	short_description = models.CharField(max_length=300)
	story = models.TextField()
	goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
	min_pledge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
	deadline = models.DateTimeField()
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
	is_featured = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	@property
	def total_raised(self):
		result = self.pledges.filter(status__in=["AUTHORIZED", "CAPTURED"]).aggregate(total=Sum("amount"))
		return result["total"] or Decimal("0.00")

	@property
	def progress_percent(self):
		if self.goal_amount <= 0:
			return 0
		return round(float((self.total_raised / self.goal_amount) * 100), 2)

	@property
	def is_live(self):
		return self.status == self.Status.ACTIVE and self.deadline > timezone.now()

	def __str__(self):
		return self.title


class CampaignMedia(models.Model):
	class MediaType(models.TextChoices):
		IMAGE = "IMAGE", "Image"
		VIDEO = "VIDEO", "Video"

	campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="media")
	media_type = models.CharField(max_length=10, choices=MediaType.choices)
	file = models.ImageField(upload_to="campaign_media/", blank=True, null=True)
	external_url = models.URLField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)


class RewardTier(models.Model):
	campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="reward_tiers")
	title = models.CharField(max_length=150)
	description = models.TextField()
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField(null=True, blank=True)
	estimated_delivery = models.DateField(null=True, blank=True)

	@property
	def claimed_count(self):
		return self.pledges.count()

	def __str__(self):
		return f"{self.title} ({self.amount})"


class CampaignUpdate(models.Model):
	campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="updates")
	title = models.CharField(max_length=200)
	content = models.TextField()
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaign_updates")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]


class CampaignComment(models.Model):
	campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="comments")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaign_comments")
	comment = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]


class FavoriteCampaign(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
	campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="favorited_by")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "campaign")
