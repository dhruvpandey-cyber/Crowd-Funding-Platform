from django.views.generic import TemplateView


class HomePageView(TemplateView):
	template_name = "frontend/home.html"


class AuthPageView(TemplateView):
	template_name = "frontend/auth.html"


class CampaignsPageView(TemplateView):
	template_name = "frontend/campaigns.html"


class CampaignDetailPageView(TemplateView):
	template_name = "frontend/campaign_detail.html"


class CreateCampaignPageView(TemplateView):
	template_name = "frontend/create_campaign.html"


class DashboardPageView(TemplateView):
	template_name = "frontend/dashboard.html"


class AdminPanelPageView(TemplateView):
	template_name = "frontend/admin_panel.html"


class AnalyticsPageView(TemplateView):
	template_name = "frontend/analytics.html"
