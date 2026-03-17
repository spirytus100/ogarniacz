from django.urls import path

from . import views


app_name = "expenses"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.expense_details, name="details"),
    path("<int:pk>/edit", views.edit_expense, name="edit"),
    path("new", views.new_expense, name="new"),
    path("<int:pk>/delete/", views.delete_expense, name="delete_expense"),
    
    path("budget/", views.budget, name="budget"),
    path("budget/new/", views.new_budget, name="new_budget"),

    path("needs/", views.needs, name="needs"),
    path("needs/<int:pk>/", views.need_details, name="need_details"),
    path("needs/<int:pk>/edit", views.edit_need, name="edit_need"),
    path("needs/new/", views.new_need, name="new_need"),
    path('needs/<int:pk>/delete/', views.delete_need, name='delete_need'),

    path("wishes/", views.wishes, name="wishes"),
    path("wishes/<int:pk>/", views.wish_details, name="wish_details"),
    path("wishes/<int:pk>/edit", views.edit_wish, name="edit_wish"),
    path("wishes/new/", views.new_wish, name="new_wish"),
    path('wishes/<int:pk>/delete/', views.delete_wish, name='delete_wish'),
]