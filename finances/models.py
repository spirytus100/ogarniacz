import datetime

from django.db import models
from django.core.validators import MinValueValidator



class InvestmentCategory(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Investment(models.Model):
    name = models.CharField(max_length=50)
    category_id = models.ForeignKey(InvestmentCategory, null=True, on_delete=models.SET_NULL)
    buy_date = models.DateField(default=datetime.date.today)
    buy_quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
    buy_price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    buy_commission = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    current_price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    current_price_date = models.DateField(blank=True, null=True)
    sell_date = models.DateField(blank=True, null=True)
    sell_quantity = models.SmallIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    sell_price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    sell_commission = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=7, decimal_places=4, validators=[MinValueValidator(0)], blank=True, null=True)
    active = models.BooleanField(default=True)
    currency = models.CharField(max_length=3)
    retirement = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class IncomeCategory(models.Model):
    name = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Income(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(IncomeCategory, null=True, on_delete=models.SET_NULL)
    date = models.DateField(default=datetime.date.today)
    value = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Cash(models.Model):
    name = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Crypto(models.Model):
    name = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.currency


class WealthChange(models.Model):
    value = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)










    




