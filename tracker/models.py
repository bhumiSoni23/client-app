from django.db import models
from django.contrib.auth.models import User


CATEGORIES = [
    ('Food', 'Food'),
    ('Travel', 'Travel'),
    ('Bills', 'Bills'),
    ('Shopping', 'Shopping'),
    ('Other', 'Other'),
]

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
