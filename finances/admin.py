from django.contrib import admin

from .models import *


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_id', 'buy_date', 'buy_quantity', 'buy_price', 'sell_date', 'sell_quantity', 'sell_price', 'interest_rate', 'active', 'exchange_rate_id']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'date', 'value']


@admin.register(Crypto)
class CryptoAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate']

@admin.register(FinancialAccount)
class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'cash', 'retirement']


admin.site.register([InvestmentCategory, IncomeCategory, WealthChange])