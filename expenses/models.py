import datetime
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class ExpensesCategories(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class CommonItem(models.Model):
    name = models.CharField(max_length=100)
    category_id = models.ForeignKey(ExpensesCategories, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    date = models.DateField(default=datetime.date.today)
    item = models.CharField(max_length=100)
    category_id = models.ForeignKey(ExpensesCategories, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.SmallIntegerField(validators=[MinValueValidator(0)])
    company = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item


class Budget(models.Model):
    category_id = models.ForeignKey(ExpensesCategories, on_delete=models.CASCADE, verbose_name='Kategoria')
    expected_cost = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], default=0.00, verbose_name='Spodziewany koszt')
    actual_cost = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], default=0.00, verbose_name='Rzeczywisty koszt')
    comment = models.CharField(max_length=200, blank=True, null=True, verbose_name='Komentarz')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def difference(self):
        expected = self.expected_cost or Decimal('0.00')
        actual = self.actual_cost or Decimal('0.00')

        return expected - actual

    def __str__(self):
        return str(self.category_id)


class BudgetResult(models.Model):
    month = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.SmallIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    budget = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    expenses = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    result = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.budget is not None and self.expenses is not None:
            self.result = self.budget - self.expenses
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.month}.{self.year}"


class BudgetResultExpenses(models.Model):
    month = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.SmallIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    budget = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    expenses = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    category_id = models.ForeignKey(ExpensesCategories, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.month}.{self.year} {self.category_id}"


class Need(models.Model):
    item = models.CharField(max_length=100)
    category_id = models.ForeignKey(ExpensesCategories, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item


class Wish(models.Model):
    item = models.CharField(max_length=100)
    category_id = models.ForeignKey(ExpensesCategories, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item
    

class Subscription(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    pay_day = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name








