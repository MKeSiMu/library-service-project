import stripe
from decouple import config
from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = (("Pending", "PENDING"), ("Paid", "PAID"))
    TYPE_CHOICES = (("Payment", "PAYMENT"), ("Fine", "FINE"))
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    borrowing_id = models.ForeignKey(
        Borrowing, on_delete=models.PROTECT, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Borrowing ID: {self.borrowing_id}; Status: {self.status}"


stripe.api_key = config("STRIPE_SECRET_KEY")


def create_checkout_session(borrowing):
    days_count = borrowing.expected_return_date - borrowing.borrow_date
    total_amount = int(borrowing.book.daily_fee * days_count.days * 100)
    session = stripe.checkout.Session.create(
        customer_email=borrowing.user.email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": total_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://127.0.0.1:8000/api/payments/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/api/payments/cancel?session_id={CHECKOUT_SESSION_ID}",
    )
    payment = Payment.objects.create(
        status="Pending",
        type="Payment",
        borrowing_id=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_amount / 100,
    )


def create_fine_checkout_session(borrowing):
    fine_multiplier = 2
    fine_days_count = borrowing.actual_return_date - borrowing.expected_return_date
    fine_amount = (
        int(borrowing.book.daily_fee * fine_days_count.days * 100) * fine_multiplier
    )
    session = stripe.checkout.Session.create(
        customer_email=borrowing.user.email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": fine_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://127.0.0.1:8000/api/payments/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/api/payments/cancel?session_id={CHECKOUT_SESSION_ID}",
        after_expiration={
            "recovery": {
                "enabled": True,
            },
        },
    )
    payment = Payment.objects.create(
        status="Pending",
        type="Fine",
        borrowing_id=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=fine_amount / 100,
    )
    return session.url
