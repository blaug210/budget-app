"""
Budget model - main container for budget items/transactions.
"""

import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class Budget(TimeStampedModel):
    """
    Budget is the main container for budget items (transactions).
    Each budget belongs to a budget group and can contain multiple items.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    changes_made = models.BooleanField(default=False)
    file_name_string = models.CharField(max_length=500, blank=True)
    list_number = models.IntegerField(null=True, blank=True)
    current_sequence_number = models.IntegerField(default=0)
    is_copy = models.BooleanField(default=False)
    is_whatif = models.BooleanField(default=False)

    # Relations
    group = models.ForeignKey(
        'BudgetGroup',
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    categories = models.ManyToManyField('Category', blank=True)
    accounting_categories = models.ManyToManyField('AccountingCategory', blank=True)
    members = models.ManyToManyField('Member', blank=True)
    sources = models.ManyToManyField('Source', blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['group', 'name']),
            models.Index(fields=['is_copy']),
            models.Index(fields=['is_whatif']),
        ]

    def __str__(self):
        return self.name

    def get_next_sequence_number(self):
        """Get the next sequence number for a new budget item."""
        self.current_sequence_number += 1
        self.save(update_fields=['current_sequence_number'])
        return self.current_sequence_number

    def get_date_range(self):
        """Get the date range of all items in this budget."""
        items = self.items.aggregate(
            min_date=models.Min('date'),
            max_date=models.Max('date')
        )
        return items['min_date'], items['max_date']

    def get_total_income(self):
        """Calculate total income for this budget (excluding beginning balances)."""
        from django.db.models import Sum, Q
        total = self.items.filter(
            monitary_value__gt=0
        ).exclude(
            Q(description__icontains='beginning balance') |
            Q(description__icontains='begin balance')
        ).aggregate(
            total=Sum('monitary_value')
        )['total']
        return total or 0

    def get_total_expenses(self):
        """Calculate total expenses for this budget."""
        from django.db.models import Sum
        total = self.items.filter(monitary_value__lt=0).aggregate(
            total=Sum('monitary_value')
        )['total']
        return total or 0

    def get_current_balance(self):
        """Get the current balance (sum of all items, excluding beginning balances)."""
        from django.db.models import Sum, Q
        total = self.items.exclude(
            Q(description__icontains='beginning balance') |
            Q(description__icontains='begin balance')
        ).aggregate(total=Sum('monitary_value'))['total']
        return total or 0
