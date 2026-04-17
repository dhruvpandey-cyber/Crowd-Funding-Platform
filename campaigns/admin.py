from django.contrib import admin

from .models import (
	Campaign,
	CampaignComment,
	CampaignMedia,
	CampaignUpdate,
	Category,
	FavoriteCampaign,
	RewardTier,
)

admin.site.register(Category)
admin.site.register(Campaign)
admin.site.register(CampaignMedia)
admin.site.register(RewardTier)
admin.site.register(CampaignUpdate)
admin.site.register(CampaignComment)
admin.site.register(FavoriteCampaign)

# Register your models here.
