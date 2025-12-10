# budget_tracker/models.py
from django.db import models
from django.conf import settings

class Transaction(models.Model):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    # Example categories - you can extend these or make Category a model
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('RENT', 'Rent'),
        ('SALARY', 'Salary'),
        ('TRANSPORT', 'Transport'),
        ('OTHER', 'Other'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='OTHER')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.owner} - {self.transaction_type} - {self.amount} on {self.date}"
