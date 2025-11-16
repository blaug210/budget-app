"""
BudgetGroup model for hierarchical organization of budgets.
"""

import uuid
from django.db import models
from apps.core.models import TimeStampedModel


class BudgetGroup(TimeStampedModel):
    """
    Hierarchical budget group for organizing budgets.
    Groups can contain subgroups and budgets.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    file_name_string = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    def get_full_path(self):
        """Get the full hierarchical path of this group."""
        if self.parent:
            return f"{self.parent.get_full_path()} / {self.name}"
        return self.name

    def get_ancestors(self):
        """Get all ancestor groups."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        """Get all descendant groups recursively."""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return descendants
