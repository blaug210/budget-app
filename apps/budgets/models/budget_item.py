"""
BudgetItem model - individual transactions/items in a budget.
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel


class BudgetItem(TimeStampedModel):
    """
    BudgetItem represents an individual transaction in a budget.
    Can be income (positive) or expense (negative).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unique_id = models.CharField(max_length=100, unique=True, db_index=True)
    sequence_number = models.IntegerField()

    # Core fields
    budget = models.ForeignKey(
        'Budget',
        on_delete=models.CASCADE,
        related_name='items'
    )
    categories = models.ManyToManyField(
        'Category',
        related_name='budget_items',
        help_text="Categories for this transaction (can have multiple)"
    )
    monitary_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Positive for income, negative for expenses"
    )
    description = models.CharField(max_length=500)

    # Dates
    date = models.DateField(db_index=True)
    posted_date = models.DateField(null=True, blank=True)
    short_date = models.CharField(max_length=50, blank=True)

    # Relations
    member = models.ForeignKey(
        'Member',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='budget_items'
    )
    source = models.ForeignKey(
        'Source',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='budget_items'
    )
    category_vendor = models.ForeignKey(
        'CategoryVendor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_items'
    )
    accounting_categories = models.ManyToManyField(
        'AccountingCategory',
        blank=True,
        related_name='budget_items'
    )

    # Tracking
    running_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Running balance after this transaction"
    )
    import_source = models.CharField(max_length=255, blank=True, default='')
    reference_number = models.CharField(max_length=100, blank=True, default='')
    update_timestamp = models.DateTimeField(auto_now=True)

    # State
    imported = models.BooleanField(default=False)
    marked = models.BooleanField(default=False)
    is_breakout = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='breakouts'
    )

    class Meta:
        ordering = ['date', 'sequence_number']
        indexes = [
            models.Index(fields=['budget', 'date']),
            models.Index(fields=['member']),
            models.Index(fields=['source']),
            models.Index(fields=['unique_id']),
            models.Index(fields=['date', 'sequence_number']),
            models.Index(fields=['imported']),
            models.Index(fields=['is_breakout']),
        ]

    def __str__(self):
        return f"{self.date} - {self.description} (${self.monitary_value})"

    def save(self, *args, **kwargs):
        """
        Override save to generate unique_id if not set
        and auto-assign sequence number.
        """
        if not self.unique_id:
            # Generate unique ID: BUDGET_ID-SEQUENCE
            if not self.sequence_number:
                self.sequence_number = self.budget.get_next_sequence_number()
            self.unique_id = f"{self.budget.id}-{self.sequence_number}"

        super().save(*args, **kwargs)

    @property
    def is_income(self):
        """Check if this item is income (positive value)."""
        return self.monitary_value > 0

    @property
    def is_expense(self):
        """Check if this item is an expense (negative value)."""
        return self.monitary_value < 0

    def get_breakout_total(self):
        """Get the total of all breakout items."""
        if not self.is_breakout:
            total = self.breakouts.aggregate(
                total=models.Sum('monitary_value')
            )['total']
            return total or 0
        return 0

    def validate_breakout(self):
        """
        Validate that breakout items sum to parent value.
        Returns True if valid, False otherwise.
        """
        if self.is_breakout:
            return True  # Breakout children don't need validation

        breakout_total = self.get_breakout_total()
        if breakout_total == 0:
            return True  # No breakouts

        return abs(breakout_total - self.monitary_value) < 0.01  # Allow small rounding errors
