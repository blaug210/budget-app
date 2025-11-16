"""
CategoryVendor model for vendor tracking and IRS reporting.
"""

import uuid
from django.db import models


class CategoryVendor(models.Model):
    """
    Vendor associated with a category, with IRS accounting text.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='vendors'
    )
    irs_accounting_text = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"
