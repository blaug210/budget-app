"""
Member model for tracking who spent/received money.
"""

import uuid
from django.db import models


class Member(models.Model):
    """
    Member represents people or entities associated with transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name
