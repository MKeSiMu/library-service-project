from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from books.permissions import IsAdminOrReadOnly
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingDetailSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = self.queryset.select_related("user", "book").filter(
                user=self.request.user
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer
