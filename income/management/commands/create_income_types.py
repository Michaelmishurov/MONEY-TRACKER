from django.core.management.base import BaseCommand
from income.models import IncomeType

class Command(BaseCommand):
    help = 'Create default income types'

    def handle(self, *args, **kwargs):
        income_types = [
            'Salary',
            'Investment',
            'Business',
            'Freelance',
            'Rental Income',
            'Pension',
            'Interest',
            'Gift',
            'Dividends',
            'Other'
        ]

        for income_type in income_types:
            IncomeType.objects.get_or_create(name=income_type)
        
        self.stdout.write(self.style.SUCCESS('Successfully created default income types'))
