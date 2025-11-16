"""
ImportTracker model for tracking import operations.
"""

import uuid
from django.db import models


class ImportTracker(models.Model):
    """
    Tracks import operations for budget items.
    Stores metadata about file imports including source, date, and statistics.
    """
    FILE_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('ofx', 'OFX/QFX'),
        ('quicken', 'Quicken'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(
        'budgets.Budget',
        on_delete=models.CASCADE,
        related_name='imports'
    )
    import_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    items_imported = models.IntegerField(default=0)
    duplicates_found = models.IntegerField(default=0)
    source_name = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-import_date']
        indexes = [
            models.Index(fields=['budget', '-import_date']),
            models.Index(fields=['file_type']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()}) - {self.import_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def success_rate(self):
        """Calculate the success rate of the import."""
        total = self.items_imported + self.duplicates_found
        if total == 0:
            return 0
        return (self.items_imported / total) * 100
