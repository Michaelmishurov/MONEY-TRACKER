from django import forms
from income.models import Income

class IncomeForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Income
        fields = ['amount', 'type', 'date', 'description']
