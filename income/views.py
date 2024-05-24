from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import IncomeForm
from .models import Income, IncomeType

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully.')
            return redirect('income:add_income')
    else:
        form = IncomeForm()
    incomes = Income.objects.filter(user=request.user)
    return render(request, 'income/add_income.html', {'form': form, 'incomes': incomes})

@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    income.delete()
    messages.success(request, 'Income deleted successfully.')
    return redirect('income:add_income')
