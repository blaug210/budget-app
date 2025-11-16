"""
BudgetItemRelation model for linking related budget items.
"""

import uuid
from django.db import models


class BudgetItemRelation(models.Model):
    """
    Represents relationships between budget items.
    Examples: linked transactions, transfers, splits, corrections.
    """
    RELATION_TYPE_CHOICES = [
        ('linked', 'Linked'),
        ('transfer', 'Transfer'),
        ('split_from', 'Split From'),
        ('correction', 'Correction'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item1 = models.ForeignKey(
        'BudgetItem',
        on_delete=models.CASCADE,
        related_name='relations_from'
    )
    item2 = models.ForeignKey(
        'BudgetItem',
        on_delete=models.CASCADE,
        related_name='relations_to'
    )
    relation_type = models.CharField(
        max_length=50,
        choices=RELATION_TYPE_CHOICES,
        default='linked'
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [['item1', 'item2', 'relation_type']]
        indexes = [
            models.Index(fields=['item1', 'relation_type']),
            models.Index(fields=['item2', 'relation_type']),
        ]

    def __str__(self):
        return f"{self.item1.description} {self.get_relation_type_display()} {self.item2.description}"
