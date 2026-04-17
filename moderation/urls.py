from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet, ReportViewSet

router = DefaultRouter()
router.register(r"reports", ReportViewSet, basename="report")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]