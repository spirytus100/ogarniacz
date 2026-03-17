from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("investments/", views.list_of_investments, name="list_of_investments"),
    path("investments/retirement/", views.retirement_investments, name="retirement_investments"),
    path("investments/<int:pk>/", views.investment_details, name="investment_details"),
    path("investments/<int:pk>/edit/", views.edit_investment, name="edit_investment"),
    path("investments/new/", views.new_investment, name="new_investment"),
    path("investments/<int:pk>/delete/", views.delete_investment, name="delete_investment"),
    path("incomes/", views.incomes, name="incomes"),
    path("incomes/new/", views.new_income, name="new_income"),
    path("incomes/<int:pk>/delete/", views.delete_income, name="delete_income"),
    path("incomes/<int:pk>/edit/", views.edit_income, name="edit_income"),
    path("incomes/<int:pk>/", views.income_details, name="income_details"),
    path("cash/", views.cash, name="cash"),
    path("cash/<int:pk>/edit/", views.edit_cash, name="edit_cash"),
]