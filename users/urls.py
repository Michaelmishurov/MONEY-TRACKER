from django.urls import path
from . import views
from django.contrib.auth import views as authViews

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('income/', views.add_income, name='add_income'),
    path('income/delete/<int:income_id>/', views.delete_income, name='delete_income'),
    path('expense/', views.add_expense, name='add_expense'),
    path('expense/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('exit/', authViews.LogoutView.as_view(next_page='/'), name='exit'),
]