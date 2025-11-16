"""
Source model for income tracking.
"""

import uuid
from django.db import models


class Source(models.Model):
    """
    Source represents income sources or transfer origins.
    """
    SOURCE_TYPE_CHOICES = [
        ('income', 'Income'),
        ('transfer', 'Transfer'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_TYPE_CHOICES,
        default='income'
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['source_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"
