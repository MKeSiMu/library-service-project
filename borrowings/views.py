import datetime

from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books.permissions import IsAdminOrReadOnly
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.select_related("user", "book")

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=int(user_id))

        if is_active is not None:
            queryset = queryset.filter(actual_return_date__isnull=True)

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_book(self, request, pk):
        """Endpoint for return borrowed book"""
        borrowing = Borrowing.objects.get(id=pk)
        if borrowing.actual_return_date is None and self.request.user == borrowing.user:
            with transaction.atomic():
                borrowing.actual_return_date = datetime.date.today()
                borrowing.save()
                return Response(
                    {"message": "You successfully returned book"},
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"message": "This book is already returned"},
            status=status.HTTP_403_FORBIDDEN,
        )
