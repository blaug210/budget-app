"""
Management command to seed the database with sample data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.budgets.models import (
    Category, Member, Source, BudgetGroup, Budget, BudgetItem
)


class Command(BaseCommand):
    help = 'Seeds the database with sample budget data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')

        # Create Categories
        categories_data = [
            'Groceries', 'Rent', 'Utilities', 'Transportation', 'Gas',
            'Dining Out', 'Entertainment', 'Healthcare', 'Shopping',
            'Salary', 'Freelance', 'Investment Income'
        ]
        categories = {}
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_name)
            categories[cat_name] = cat
            if created:
                self.stdout.write(f'  ✓ Created category: {cat_name}')

        # Create Members
        members_data = ['You', 'Spouse', 'Family']
        members = {}
        for mem_name in members_data:
            mem, created = Member.objects.get_or_create(name=mem_name)
            members[mem_name] = mem
            if created:
                self.stdout.write(f'  ✓ Created member: {mem_name}')

        # Create Sources
        sources_data = [
            ('Main Job', 'income'),
            ('Side Hustle', 'income'),
            ('Investments', 'income'),
        ]
        sources = {}
        for source_name, source_type in sources_data:
            src, created = Source.objects.get_or_create(
                name=source_name,
                defaults={'source_type': source_type}
            )
            sources[source_name] = src
            if created:
                self.stdout.write(f'  ✓ Created source: {source_name}')

        # Create Budget Group
        group, created = BudgetGroup.objects.get_or_create(
            name='2025',
            defaults={'file_name_string': '/budgets/2025'}
        )
        if created:
            self.stdout.write(f'  ✓ Created budget group: 2025')

        # Create Budget
        budget, created = Budget.objects.get_or_create(
            name='January 2025',
            defaults={
                'group': group,
                'file_name_string': '/budgets/2025/january'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created budget: January 2025')

        # Create Transactions
        transactions = [
            # Income
            {'days_ago': 30, 'desc': 'Monthly Salary', 'amount': 4500, 'cat': 'Salary', 'mem': 'You', 'src': 'Main Job'},
            {'days_ago': 25, 'desc': 'Freelance Project', 'amount': 800, 'cat': 'Freelance', 'mem': 'You', 'src': 'Side Hustle'},
            {'days_ago': 15, 'desc': 'Dividend Payment', 'amount': 150, 'cat': 'Investment Income', 'mem': 'You', 'src': 'Investments'},

            # Expenses
            {'days_ago': 29, 'desc': 'Monthly Rent', 'amount': -1500, 'cat': 'Rent', 'mem': 'You'},
            {'days_ago': 28, 'desc': 'Electric Bill', 'amount': -120, 'cat': 'Utilities', 'mem': 'You'},
            {'days_ago': 28, 'desc': 'Internet Service', 'amount': -60, 'cat': 'Utilities', 'mem': 'You'},
            {'days_ago': 27, 'desc': 'Grocery Shopping', 'amount': -185.50, 'cat': 'Groceries', 'mem': 'You'},
            {'days_ago': 26, 'desc': 'Gas Station', 'amount': -45.00, 'cat': 'Gas', 'mem': 'You'},
            {'days_ago': 24, 'desc': 'Dinner at Restaurant', 'amount': -75.25, 'cat': 'Dining Out', 'mem': 'Family'},
            {'days_ago': 23, 'desc': 'Grocery Shopping', 'amount': -142.80, 'cat': 'Groceries', 'mem': 'Spouse'},
            {'days_ago': 22, 'desc': 'Movie Tickets', 'amount': -35.00, 'cat': 'Entertainment', 'mem': 'Family'},
            {'days_ago': 20, 'desc': 'Gas Station', 'amount': -50.00, 'cat': 'Gas', 'mem': 'You'},
            {'days_ago': 19, 'desc': 'Doctor Visit Co-pay', 'amount': -30.00, 'cat': 'Healthcare', 'mem': 'You'},
            {'days_ago': 18, 'desc': 'Grocery Shopping', 'amount': -98.40, 'cat': 'Groceries', 'mem': 'You'},
            {'days_ago': 17, 'desc': 'Online Shopping', 'amount': -125.00, 'cat': 'Shopping', 'mem': 'Spouse'},
            {'days_ago': 15, 'desc': 'Coffee Shop', 'amount': -12.50, 'cat': 'Dining Out', 'mem': 'You'},
            {'days_ago': 14, 'desc': 'Gas Station', 'amount': -48.75, 'cat': 'Gas', 'mem': 'You'},
            {'days_ago': 13, 'desc': 'Grocery Shopping', 'amount': -167.30, 'cat': 'Groceries', 'mem': 'Spouse'},
            {'days_ago': 12, 'desc': 'Pharmacy', 'amount': -25.00, 'cat': 'Healthcare', 'mem': 'Family'},
            {'days_ago': 10, 'desc': 'Lunch Out', 'amount': -28.00, 'cat': 'Dining Out', 'mem': 'You'},
            {'days_ago': 9, 'desc': 'Streaming Services', 'amount': -45.00, 'cat': 'Entertainment', 'mem': 'You'},
            {'days_ago': 7, 'desc': 'Gas Station', 'amount': -52.00, 'cat': 'Gas', 'mem': 'You'},
            {'days_ago': 6, 'desc': 'Grocery Shopping', 'amount': -203.15, 'cat': 'Groceries', 'mem': 'You'},
            {'days_ago': 5, 'desc': 'Clothing Store', 'amount': -89.99, 'cat': 'Shopping', 'mem': 'Spouse'},
            {'days_ago': 3, 'desc': 'Weekend Brunch', 'amount': -65.50, 'cat': 'Dining Out', 'mem': 'Family'},
            {'days_ago': 2, 'desc': 'Grocery Shopping', 'amount': -78.20, 'cat': 'Groceries', 'mem': 'You'},
            {'days_ago': 1, 'desc': 'Gas Station', 'amount': -46.00, 'cat': 'Gas', 'mem': 'You'},
        ]

        today = timezone.now().date()
        for trans_data in transactions:
            date = today - timedelta(days=trans_data['days_ago'])

            BudgetItem.objects.create(
                budget=budget,
                date=date,
                description=trans_data['desc'],
                monitary_value=Decimal(str(trans_data['amount'])),
                category=categories[trans_data['cat']],
                member=members.get(trans_data.get('mem', 'You')),
                source=sources.get(trans_data.get('src')) if 'src' in trans_data else None,
            )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {len(transactions)} transactions!'))
        self.stdout.write(self.style.SUCCESS('\n📊 Sample Data Summary:'))
        self.stdout.write(f'   • Categories: {len(categories)}')
        self.stdout.write(f'   • Members: {len(members)}')
        self.stdout.write(f'   • Sources: {len(sources)}')
        self.stdout.write(f'   • Budget Groups: 1')
        self.stdout.write(f'   • Budgets: 1')
        self.stdout.write(f'   • Transactions: {len(transactions)}')
        self.stdout.write(self.style.SUCCESS('\n✨ Your budget app is ready to explore!'))
        self.stdout.write('   Visit: http://localhost:8000')
