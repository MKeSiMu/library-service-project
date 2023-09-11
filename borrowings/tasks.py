import datetime

from decouple import config

from borrowings.bot import bot
from borrowings.models import Borrowing

from celery import shared_task


@shared_task
def overdue_borrowings_check():
    overdue_borrowings = Borrowing.objects.select_related("user", "book").filter(
        actual_return_date__isnull=True,
        expected_return_date__lte=datetime.date.today() + datetime.timedelta(days=1),
    )
    if overdue_borrowings:
        for overdue_borrowing in overdue_borrowings:
            bot.send_message(
                config("CHAT_ID"),
                f"{overdue_borrowing.user} still not return '{overdue_borrowing.book.title}' "
                f"book on {overdue_borrowing.expected_return_date}",
            )
    if not overdue_borrowings:
        bot.send_message(config("CHAT_ID"), "No borrowings overdue today!")
