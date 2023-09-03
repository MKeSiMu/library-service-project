from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        actual_return_date = attrs.get("password", "")

        if actual_return_date == "":
            Borrowing.validate_book_inventory(
                attrs["book"].inventory,
                attrs["book"].title,
                serializers.ValidationError,
            )

        data = super(BorrowingSerializer, self).validate(attrs)

        Borrowing.validate_expected_return_date(
            attrs["expected_return_date"],
            serializers.ValidationError,
        )

        if actual_return_date != "":
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
