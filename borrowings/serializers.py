from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        borrow_date = attrs.get("borrow_date", None)
        actual_return_date = attrs.get("actual_return_date", None)

        if actual_return_date is None:
            Borrowing.validate_book_inventory(
                borrow_date,
                attrs["book"].inventory,
                attrs["book"].title,
                serializers.ValidationError,
            )

        data = super(BorrowingSerializer, self).validate(attrs)

        Borrowing.validate_expected_return_date(
            borrow_date,
            attrs["expected_return_date"],
            serializers.ValidationError,
        )

        if actual_return_date is not None:
            Borrowing.validate_actual_return_date(
                attrs["expected_return_date"],
                attrs["actual_return_date"],
                serializers.ValidationError,
            )

        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = (
            "id",
            "actual_return_date",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)


class BorrowingReturnSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",)
        read_only_fields = ("id",)
