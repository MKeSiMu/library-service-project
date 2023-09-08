from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentDetailSerializer


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
