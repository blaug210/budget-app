"""
AccountingCategory model for cost accounting and IRS reporting.
"""

import uuid
from django.db import models


class AccountingCategory(models.Model):
    """
    Accounting category for cost accounting and tax reporting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Accounting Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name
