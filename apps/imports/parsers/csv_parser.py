"""
CSV parser for importing budget transactions.
"""
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any
from io import StringIO


class CSVParser:
    """Parse CSV files to extract budget transaction data."""

    def __init__(self, file_content: str):
        """
        Initialize the CSV parser.

        Args:
            file_content: The CSV file content as a string
        """
        self.file_content = file_content
        self.errors = []
        self.warnings = []

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the CSV content and return a list of transaction dictionaries.

        Returns:
            List of transaction dictionaries with keys: date, description, amount, category, member
        """
        transactions = []

        try:
            # Read CSV content
            csv_file = StringIO(self.file_content)
            reader = csv.DictReader(csv_file)

            # Validate headers
            expected_headers = {'date', 'description', 'amount', 'category'}
            optional_headers = {'member', 'source', 'reference_number'}

            if not reader.fieldnames:
                self.errors.append("CSV file is empty or has no headers")
                return []

            headers = set(h.lower().strip() for h in reader.fieldnames)

            if not expected_headers.issubset(headers):
                missing = expected_headers - headers
                self.errors.append(f"Missing required columns: {', '.join(missing)}")
                return []

            # Parse each row
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is headers
                try:
                    transaction = self._parse_row(row, row_num)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    self.errors.append(f"Row {row_num}: {str(e)}")

        except csv.Error as e:
            self.errors.append(f"CSV parsing error: {str(e)}")
        except Exception as e:
            self.errors.append(f"Unexpected error: {str(e)}")

        return transactions

    def _parse_row(self, row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """
        Parse a single CSV row into a transaction dictionary.

        Args:
            row: Dictionary of CSV row data
            row_num: Row number for error reporting

        Returns:
            Transaction dictionary or None if row is invalid
        """
        # Normalize keys (lowercase and strip whitespace)
        row = {k.lower().strip(): v.strip() for k, v in row.items()}

        # Skip empty rows
        if all(not v for v in row.values()):
            return None

        transaction = {}

        # Parse date (required)
        date_str = row.get('date', '')
        if not date_str:
            self.errors.append(f"Row {row_num}: Date is required")
            return None

        transaction['date'] = self._parse_date(date_str, row_num)
        if not transaction['date']:
            return None

        # Parse description (required)
        description = row.get('description', '').strip()
        if not description:
            self.errors.append(f"Row {row_num}: Description is required")
            return None
        transaction['description'] = description

        # Parse amount (required)
        amount_str = row.get('amount', '')
        if not amount_str:
            self.errors.append(f"Row {row_num}: Amount is required")
            return None

        transaction['amount'] = self._parse_amount(amount_str, row_num)
        if transaction['amount'] is None:
            return None

        # Parse category (required)
        category = row.get('category', '').strip()
        if not category:
            self.errors.append(f"Row {row_num}: Category is required")
            return None
        transaction['category'] = category

        # Parse optional fields
        transaction['member'] = row.get('member', '').strip() or None
        transaction['source'] = row.get('source', '').strip() or None
        transaction['reference_number'] = row.get('reference_number', '').strip() or ''

        return transaction

    def _parse_date(self, date_str: str, row_num: int) -> datetime.date:
        """Parse date string into date object."""
        date_formats = [
            '%Y-%m-%d',      # 2024-11-22
            '%m/%d/%Y',      # 11/22/2024
            '%d/%m/%Y',      # 22/11/2024
            '%Y/%m/%d',      # 2024/11/22
            '%m-%d-%Y',      # 11-22-2024
            '%d-%m-%Y',      # 22-11-2024
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        self.errors.append(f"Row {row_num}: Invalid date format '{date_str}'. Use YYYY-MM-DD or MM/DD/YYYY")
        return None

    def _parse_amount(self, amount_str: str, row_num: int) -> Decimal:
        """Parse amount string into Decimal."""
        # Remove currency symbols and commas
        amount_str = amount_str.replace('$', '').replace(',', '').strip()

        try:
            amount = Decimal(amount_str)
            return amount
        except (InvalidOperation, ValueError):
            self.errors.append(f"Row {row_num}: Invalid amount '{amount_str}'")
            return None

    def has_errors(self) -> bool:
        """Check if any errors occurred during parsing."""
        return len(self.errors) > 0

    def get_errors(self) -> List[str]:
        """Get list of all parsing errors."""
        return self.errors

    def get_warnings(self) -> List[str]:
        """Get list of all parsing warnings."""
        return self.warnings
