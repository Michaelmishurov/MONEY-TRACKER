from django.db import models
from django.contrib.auth.models import User
from expenses.models import ExpenseCategory
from income.models import IncomeType

class AnalyticsOverview(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Overview for {self.user.username}"

class AnalyticsCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.category.name} - {self.total_spent}"

class AnalyticsTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.date} - Income: {self.total_income}, Expense: {self.total_expense}"
