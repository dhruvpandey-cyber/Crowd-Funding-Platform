import uuid

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment, PayoutRequest, Refund
from .serializers import PaymentSerializer, PayoutRequestSerializer, RefundSerializer
from pledges.models import Pledge


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = PaymentSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		if self.request.user.is_staff:
			return Payment.objects.select_related("pledge").all()
		return Payment.objects.select_related("pledge").filter(pledge__backer=self.request.user)


class RefundViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = RefundSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		if self.request.user.is_staff:
			return Refund.objects.select_related("payment", "payment__pledge").all()
		return Refund.objects.select_related("payment", "payment__pledge").filter(
			payment__pledge__backer=self.request.user
		)


class PayoutRequestViewSet(viewsets.ModelViewSet):
	serializer_class = PayoutRequestSerializer
	permission_classes = [permissions.IsAuthenticated]
	filterset_fields = ["status", "campaign"]

	def get_queryset(self):
		if self.request.user.is_staff:
			return PayoutRequest.objects.select_related("creator", "campaign").all()
		return PayoutRequest.objects.select_related("creator", "campaign").filter(creator=self.request.user)

	def perform_create(self, serializer):
		serializer.save(creator=self.request.user)


class SandboxCheckoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		pledge_id = request.data.get("pledge_id")
		gateway = request.data.get("gateway", "sandbox")

		try:
			pledge = Pledge.objects.get(id=pledge_id, backer=request.user)
		except Pledge.DoesNotExist:
			return Response({"detail": "Pledge not found."}, status=status.HTTP_404_NOT_FOUND)

		if hasattr(pledge, "payment"):
			return Response({"detail": "Payment already exists for this pledge."}, status=status.HTTP_400_BAD_REQUEST)

		payment = Payment.objects.create(
			pledge=pledge,
			gateway=gateway,
			transaction_id=f"TXN-{uuid.uuid4().hex[:16].upper()}",
			amount=pledge.amount,
			status=Payment.Status.SUCCESS,
			paid_at=timezone.now(),
		)
		pledge.status = Pledge.Status.CAPTURED
		pledge.payment_reference = payment.transaction_id
		pledge.save(update_fields=["status", "payment_reference", "updated_at"])

		return Response(
			{
				"detail": "Sandbox payment captured successfully.",
				"payment_id": payment.id,
				"transaction_id": payment.transaction_id,
			},
			status=status.HTTP_201_CREATED,
		)


class SandboxRefundView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		payment_id = request.data.get("payment_id")
		reason = request.data.get("reason", "Requested by user")

		try:
			payment = Payment.objects.select_related("pledge").get(id=payment_id, pledge__backer=request.user)
		except Payment.DoesNotExist:
			return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

		refund = Refund.objects.create(
			payment=payment,
			amount=payment.amount,
			reason=reason,
			status=Refund.Status.PROCESSED,
		)
		payment.pledge.status = Pledge.Status.REFUNDED
		payment.pledge.save(update_fields=["status", "updated_at"])

		return Response(
			{
				"detail": "Sandbox refund processed.",
				"refund_id": refund.id,
			},
			status=status.HTTP_201_CREATED,
		)
