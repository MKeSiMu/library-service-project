from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import (
    BookSerializer,
    BookListSerializer,
    BookDetailSerializer
)


class BookPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = BookPagination

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        if self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer
