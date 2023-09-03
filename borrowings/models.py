import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import CheckConstraint, Q, F

from books.models import Book
from library_service_project import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="borrowings"
    )

    class Meta:
        ordering = ["borrow_date"]

    def __str__(self):
        return f"{self.borrow_date}"

    @staticmethod
    def validate_expected_return_date(expected_return_date, error_to_raise):
        if not (expected_return_date > datetime.date.today()):
            raise error_to_raise(
                {
                    "expected_return_date": (
                        "Expected return date should be greater than borrow date"
                    )
                }
            )

    @staticmethod
    def validate_actual_return_date(
        expected_return_date, actual_return_date, error_to_raise
    ):
        if actual_return_date:
            if not (actual_return_date >= expected_return_date):
                raise error_to_raise(
                    {
                        "actual_return_date": (
                            "Actual return date should be greater or equal to expected return date"
                        )
                    }
                )

    def clean(
        self, force_insert=False, force_update=False, using=None, update_field=None
    ):
        Borrowing.validate_expected_return_date(
            self.expected_return_date, ValidationError
        )
        if self.actual_return_date:
            Borrowing.validate_actual_return_date(
                self.expected_return_date, self.actual_return_date, ValidationError
            )

    def save(
        self, force_insert=False, force_update=False, using=None, update_field=None
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_field
        )
