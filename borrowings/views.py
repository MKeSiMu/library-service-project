import datetime

from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)
from payments.models import create_fine_checkout_session


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        unpaid_payments_count = Borrowing.objects.filter(
            user=self.request.user.id, payments__status__exact="Pending"
        ).count()

        if unpaid_payments_count > 0:
            return Response(
                {
                    "message": "You have unpaid fees. Please pay first and then you can borrow new books."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = self.queryset.select_related("user", "book").prefetch_related("payments")

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=int(user_id))

        if is_active == "true":
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

                if borrowing.actual_return_date > borrowing.expected_return_date:
                    create_fine_checkout_session(borrowing)

                    return Response(
                        {
                            "message": (
                                f"Thank you for returning the book! "
                                f"But you still have to pay a fine for days of overdue."
                            )
                        },
                        status=status.HTTP_200_OK,
                    )

                if borrowing.actual_return_date == borrowing.expected_return_date:
                    return Response(
                        {"message": "You successfully returned book"},
                        status=status.HTTP_200_OK,
                    )
        return Response(
            {"message": "This book is already returned"},
            status=status.HTTP_403_FORBIDDEN,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                type=int,
                description="If user is_staff, filter by User id(ex. ?user_id=1)"
            ),
            OpenApiParameter(
                "is_active",
                type=str,
                description="filtering by active borrowings (still not returned)(ex. ?is_active=true)"
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
