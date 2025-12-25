"""
Import service for bulk importing transactions.
"""
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from django.db import transaction
from django.db.models import Q

from apps.budgets.models import (
    Budget,
    BudgetItem,
    Category,
    Member,
    Source,
)
from apps.imports.models import ImportTracker


class ImportService:
    """Service for importing transactions from parsed data."""

    def __init__(self, budget: Budget):
        """
        Initialize the import service.

        Args:
            budget: The budget to import transactions into
        """
        self.budget = budget
        self.stats = {
            'total': 0,
            'imported': 0,
            'duplicates': 0,
            'errors': 0,
            'skipped': 0,
        }
        self.errors = []
        self.duplicates = []

    def import_transactions(
        self,
        transactions: List[Dict[str, Any]],
        file_name: str,
        file_type: str = 'csv'
    ) -> Dict[str, Any]:
        """
        Import a list of transactions into the budget.

        Args:
            transactions: List of transaction dictionaries from parser
            file_name: Name of the imported file
            file_type: Type of file (csv or xml)

        Returns:
            Dictionary with import statistics and results
        """
        self.stats['total'] = len(transactions)

        with transaction.atomic():
            # Create import tracker
            import_tracker = ImportTracker.objects.create(
                budget=self.budget,
                file_name=file_name,
                file_type=file_type,
                items_imported=0,
                duplicates_found=0,
                source_name=f"Bulk Upload: {file_name}"
            )

            imported_items = []

            for idx, trans_data in enumerate(transactions, start=1):
                # Use savepoint for each transaction so errors don't break the whole import
                try:
                    with transaction.atomic():
                        # Check for duplicates
                        if self._is_duplicate(trans_data):
                            self.stats['duplicates'] += 1
                            self.duplicates.append({
                                'row': idx,
                                'description': trans_data.get('description'),
                                'date': trans_data.get('date'),
                                'amount': trans_data.get('amount'),
                            })
                            continue

                        # Get or create category
                        category = self._get_or_create_category(trans_data.get('category'))
                        if not category:
                            self.errors.append(f"Row {idx}: Could not create category '{trans_data.get('category')}'")
                            self.stats['errors'] += 1
                            continue

                        # Get or create member (optional)
                        member = None
                        if trans_data.get('member'):
                            member = self._get_or_create_member(trans_data.get('member'))

                        # Get or create source (optional)
                        source = None
                        if trans_data.get('source'):
                            source = self._get_or_create_source(trans_data.get('source'))

                        # Get next sequence number
                        sequence_number = self.budget.get_next_sequence_number()

                        # Create budget item
                        item = BudgetItem.objects.create(
                            budget=self.budget,
                            member=member,
                            source=source,
                            date=trans_data['date'],
                            posted_date=trans_data['date'],
                            description=trans_data['description'],
                            monitary_value=Decimal(str(trans_data['amount'])),
                            sequence_number=sequence_number,
                            unique_id=f"IMP-{import_tracker.pk}-{sequence_number}",
                            imported=True,
                            import_source=file_name,
                            reference_number=trans_data.get('reference_number', ''),
                        )

                        # Add category to many-to-many relationship
                        if category:
                            item.categories.add(category)

                        imported_items.append(item)
                        self.stats['imported'] += 1

                except Exception as e:
                    self.errors.append(f"Row {idx}: {str(e)}")
                    self.stats['errors'] += 1

            # Update import tracker
            import_tracker.items_imported = self.stats['imported']
            import_tracker.duplicates_found = self.stats['duplicates']
            import_tracker.save()

            # Recalculate running balances
            self._recalculate_running_balances()

        return {
            'success': self.stats['errors'] == 0 or self.stats['imported'] > 0,
            'stats': self.stats,
            'errors': self.errors,
            'duplicates': self.duplicates,
            'import_tracker_id': import_tracker.pk,
        }

    def _is_duplicate(self, trans_data: Dict[str, Any]) -> bool:
        """
        Check if a transaction already exists in the budget.

        A duplicate is defined as having the same date, amount, and description.
        """
        return BudgetItem.objects.filter(
            budget=self.budget,
            date=trans_data['date'],
            monitary_value=Decimal(str(trans_data['amount'])),
            description=trans_data['description']
        ).exists()

    def _get_or_create_category(self, category_name: str) -> Category:
        """Get or create a category by name."""
        if not category_name:
            return None

        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Auto-created from import'}
        )

        # Add category to budget's categories if not already there
        if category not in self.budget.categories.all():
            self.budget.categories.add(category)

        return category

    def _get_or_create_member(self, member_name: str) -> Member:
        """Get or create a member by name."""
        if not member_name:
            return None

        member, created = Member.objects.get_or_create(name=member_name)

        # Add member to budget's members if not already there
        if member not in self.budget.members.all():
            self.budget.members.add(member)

        return member

    def _get_or_create_source(self, source_name: str) -> Source:
        """Get or create a source by name."""
        if not source_name:
            return None

        source, created = Source.objects.get_or_create(
            name=source_name,
            defaults={'source_type': 'income'}  # Default to income
        )

        # Add source to budget's sources if not already there
        if source not in self.budget.sources.all():
            self.budget.sources.add(source)

        return source

    def _recalculate_running_balances(self):
        """Recalculate running balances for all budget items."""
        items = BudgetItem.objects.filter(budget=self.budget).order_by('date', 'sequence_number')

        running_balance = Decimal('0.00')
        for item in items:
            running_balance += item.monitary_value
            item.running_balance = running_balance
            item.save(update_fields=['running_balance'])
