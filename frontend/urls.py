from django.urls import path

from .views import (
    AdminPanelPageView,
    AnalyticsPageView,
    AuthPageView,
    CampaignDetailPageView,
    CampaignsPageView,
    CreateCampaignPageView,
    DashboardPageView,
    HomePageView,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("auth/", AuthPageView.as_view(), name="auth-page"),
    path("campaigns/", CampaignsPageView.as_view(), name="campaigns-page"),
    path("campaigns/<int:campaign_id>/", CampaignDetailPageView.as_view(), name="campaign-detail-page"),
    path("create/", CreateCampaignPageView.as_view(), name="create-campaign-page"),
    path("dashboard/", DashboardPageView.as_view(), name="dashboard-page"),
    path("analytics/", AnalyticsPageView.as_view(), name="analytics-page"),
    path("admin-panel/", AdminPanelPageView.as_view(), name="admin-panel-page"),
]
