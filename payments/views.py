import stripe
from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "borrowing_id__user", "borrowing_id__book"
        )

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing_id__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
        permission_classes=[IsAuthenticated],
    )
    def success(self, request):
        """Endpoint for success payment"""
        session_id = self.request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        payment.status = "Paid"
        payment.save()
        return Response(
            {"message": f"Successful payment! Thank you, {payment.borrowing_id.user}"},
            status=status.HTTP_200_OK,
        )
