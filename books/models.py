from django.db import models


class Book(models.Model):
    COVER_CHOICES = (("H", "HARD"), ("S", "SOFT"))
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=1, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.author})"

    def decrease_book_inventory(self):
        self.inventory -= 1
        self.save()

    def increase_book_inventory(self):
        self.inventory += 1
        self.save()
