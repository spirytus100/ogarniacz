from django.contrib import admin

from .models import CommonItem, Expense, Budget, Need, Wish, ExpensesCategories, BudgetResult, BudgetResultExpenses



@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['item', 'expense_date', 'category_id', 'price', 'quantity', 'company']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'expected_cost', 'actual_cost', 'comment']


@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = ['item', 'category_id', 'price']


admin.site.register([CommonItem, Wish, ExpensesCategories, BudgetResult, BudgetResultExpenses])

