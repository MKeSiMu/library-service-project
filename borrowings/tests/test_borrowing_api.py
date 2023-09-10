import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer, BookListSerializer
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id: int):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": "Soft",
        "inventory": 5,
        "daily_fee": 0.60

    }

    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    defaults = {
        "expected_return_date": datetime.date.today() + datetime.timedelta(days=2),
        "book": sample_book(),
    }

    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@teset.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_return_only_user_list_borrowings(self):
        another_user = get_user_model().objects.create_user(
            "new_test@teset.com",
            "new_testpass"
        )
        authenticated_user_borrowing = sample_borrowing(
            user=self.user
        )
        another_user_borrowing = sample_borrowing(
            user=another_user
        )

        res = self.client.get(BORROWING_URL)

        serializer1 = BorrowingSerializer(authenticated_user_borrowing)
        serializer2 = BorrowingSerializer(another_user_borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_create_borrowing_with_payment(self):
        payload = {
            "expected_return_date": datetime.date.today() + datetime.timedelta(days=2),
            "book": sample_book().id,
            "user": self.user.id
        }

        res = self.client.post(BORROWING_URL, payload)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.data["payments"]), 1)
        for key in payload:
            if key == "book":
                self.assertEqual(payload[key], borrowing.id)
            if key == "user":
                self.assertEqual(payload[key], borrowing.user.id)
            if key != "book" and key != "user":
                self.assertEqual(payload[key], getattr(borrowing, key))


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_return_all_user_list_borrowings(self):
        another_user = get_user_model().objects.create_user(
            "new_test@teset.com",
            "new_testpass"
        )
        authenticated_admin_user_borrowing = sample_borrowing(
            user=self.user
        )
        another_user_borrowing = sample_borrowing(
            user=another_user
        )

        res = self.client.get(BORROWING_URL)

        serializer1 = BorrowingSerializer(authenticated_admin_user_borrowing)
        serializer2 = BorrowingSerializer(another_user_borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])

    def test_delete_borrowing_not_allowed(self):
        borrowing = sample_borrowing(
            user=self.user
        )

        url = detail_url(borrowing.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
