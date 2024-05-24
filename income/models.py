from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class IncomeType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.ForeignKey(IncomeType, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.amount} - {self.type.name}"
