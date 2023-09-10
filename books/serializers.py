from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    daily_fee = serializers.FloatField()

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "inventory")


class BookDetailSerializer(BookSerializer):
    cover = serializers.CharField(source="get_cover_display")
