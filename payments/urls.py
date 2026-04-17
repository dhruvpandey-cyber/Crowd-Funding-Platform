from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, PayoutRequestViewSet, RefundViewSet, SandboxCheckoutView, SandboxRefundView

router = DefaultRouter()
router.register(r"transactions", PaymentViewSet, basename="payment")
router.register(r"refunds", RefundViewSet, basename="refund")
router.register(r"payout-requests", PayoutRequestViewSet, basename="payout-request")

urlpatterns = [
    path("sandbox/checkout/", SandboxCheckoutView.as_view(), name="sandbox-checkout"),
    path("sandbox/refund/", SandboxRefundView.as_view(), name="sandbox-refund"),
    path("", include(router.urls)),
]