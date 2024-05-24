from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from income.models import Income, IncomeType
from .forms import IncomeForm
from expenses.forms import ExpenseForm
from expenses.models import Expense
from django.db.models import Sum
from analytics.models import AnalyticsOverview, AnalyticsCategory, AnalyticsTime, ExpenseCategory
from datetime import datetime, timedelta
from decimal import Decimal

import logging

logger = logging.getLogger('mylogger')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                
                # Create AnalyticsOverview for the new user
                AnalyticsOverview.objects.create(user=user)
                
                messages.success(request, 'Account created successfully. Please log in.')
                return redirect('/users/login/')
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'registration/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in')
            return redirect('users:profile')  # Перенаправлення на profile
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login/login.html')

def main(request):
    return render(request, 'main/main.html')

@login_required
def profile(request):
    income_form = IncomeForm()
    expense_form = ExpenseForm()
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    # Update analytics before fetching them
    update_analytics(request.user)

    # Calculate analytics
    overview = AnalyticsOverview.objects.get(user=request.user)
    categories = AnalyticsCategory.objects.filter(user=request.user)
    all_times = AnalyticsTime.objects.filter(user=request.user).order_by('date')  # All-time data

    # Filter by month if requested
    selected_month = request.GET.get('month')
    daily_data = []
    if selected_month:
        month = datetime.strptime(selected_month, "%Y-%m").date()
        incomes = incomes.filter(date__year=month.year, date__month=month.month)
        expenses = expenses.filter(date__year=month.year, date__month=month.month)
        daily_data = prepare_daily_data(incomes, expenses)

    # Debug print
    logger.debug(f"User: {request.user}")
    logger.debug(f"Incomes: {list(incomes)}")
    logger.debug(f"Expenses: {list(expenses)}")
    logger.debug(f"Overview: {overview}")
    logger.debug(f"Categories: {list(categories)}")
    logger.debug(f"All Times: {list(all_times)}")
    logger.debug(f"Daily Data: {daily_data}")

    return render(request, 'profile/profile.html', {
        'user': request.user,
        'income_form': income_form,
        'expense_form': expense_form,
        'incomes': incomes,
        'expenses': expenses,
        'overview': overview,
        'categories': categories,
        'all_times': all_times,  # All-time data for the second graph
        'selected_month': selected_month,
        'daily_data': daily_data,
    })


def prepare_daily_data(incomes, expenses):
    daily_data = {}
    for income in incomes:
        date_str = income.date.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {'income': 0, 'expense': 0}
        daily_data[date_str]['income'] += float(income.amount)

    for expense in expenses:
        date_str = expense.date.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {'income': 0, 'expense': 0}
        daily_data[date_str]['expense'] += float(expense.amount)

    # Convert to list of dicts sorted by date
    daily_data = [{'date': date, 'income': data['income'], 'expense': data['expense']} for date, data in sorted(daily_data.items())]
    return daily_data


def update_analytics(user):
    # Overview
    total_income = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0.00
    total_expense = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0.00
    balance = total_income - total_expense

    overview, created = AnalyticsOverview.objects.get_or_create(user=user)
    overview.total_income = total_income
    overview.total_expense = total_expense
    overview.balance = balance
    overview.save()

    # Categories
    expense_categories = ExpenseCategory.objects.all()
    for category in expense_categories:
        total_spent = Expense.objects.filter(user=user, category=category).aggregate(total=Sum('amount'))['total'] or 0.00
        category_analytics, created = AnalyticsCategory.objects.get_or_create(user=user, category=category)
        category_analytics.total_spent = total_spent
        category_analytics.save()

    # Time-based
    today = datetime.today()
    start_date = today - timedelta(days=3*30)  # 3 months ago
    date = start_date
    while date <= today:
        total_income = Income.objects.filter(user=user, date__year=date.year, date__month=date.month).aggregate(total=Sum('amount'))['total'] or 0.00
        total_expense = Expense.objects.filter(user=user, date__year=date.year, date__month=date.month).aggregate(total=Sum('amount'))['total'] or 0.00
        time_analytics, created = AnalyticsTime.objects.get_or_create(user=user, date=date.replace(day=1))
        time_analytics.total_income = total_income
        time_analytics.total_expense = total_expense
        time_analytics.save()
        date += timedelta(days=30)  # Move to the next month

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully.')
            return redirect('users:profile')
    return redirect('users:profile')

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully.')
    return redirect('users:profile')

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('users:profile')
    return redirect('users:profile')

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('users:profile')

@login_required
def analytics(request):
    update_analytics(request.user)
    overview = get_object_or_404(AnalyticsOverview, user=request.user)
    categories = AnalyticsCategory.objects.filter(user=request.user)
    times = AnalyticsTime.objects.filter(user=request.user)
    return render(request, 'analytics/analytics.html', {
        'overview': overview,
        'categories': categories,
        'times': times,
    })

def update_analytics(user):
    # Overview
    total_income = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0.00
    total_expense = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0.00
    balance = Decimal(total_income) - Decimal(total_expense)
    overview, created = AnalyticsOverview.objects.get_or_create(user=user)
    overview.total_income = total_income
    overview.total_expense = total_expense
    overview.balance = balance
    overview.save()

    # Categories
    expense_categories = ExpenseCategory.objects.all()
    for category in expense_categories:
        total_spent = Expense.objects.filter(user=user, category=category).aggregate(total=Sum('amount'))['total'] or 0.00
        category_analytics, created = AnalyticsCategory.objects.get_or_create(user=user, category=category)
        category_analytics.total_spent = total_spent
        category_analytics.save()

    # Time-based
    today = datetime.today()
    for i in range(1, 4):
        date = today - timedelta(days=i*30)
        month = date.month
        year = date.year
        total_income = Income.objects.filter(user=user, date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0.00
        total_expense = Expense.objects.filter(user=user, date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0.00
        time_analytics, created = AnalyticsTime.objects.get_or_create(user=user, date=date.replace(day=1))
        time_analytics.total_income = total_income
        time_analytics.total_expense = total_expense
        time_analytics.save()