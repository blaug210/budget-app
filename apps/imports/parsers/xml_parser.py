"""
XML parser for importing budget transactions.
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any


class XMLParser:
    """Parse XML files to extract budget transaction data."""

    def __init__(self, file_content: str):
        """
        Initialize the XML parser.

        Args:
            file_content: The XML file content as a string
        """
        self.file_content = file_content
        self.errors = []
        self.warnings = []

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the XML content and return a list of transaction dictionaries.

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        try:
            root = ET.fromstring(self.file_content)

            # Find all transaction elements
            transaction_elements = root.findall('.//transaction')

            if not transaction_elements:
                self.errors.append("No transactions found in XML file")
                return []

            for idx, trans_elem in enumerate(transaction_elements, start=1):
                try:
                    transaction = self._parse_transaction(trans_elem, idx)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    self.errors.append(f"Transaction {idx}: {str(e)}")

        except ET.ParseError as e:
            self.errors.append(f"XML parsing error: {str(e)}")
        except Exception as e:
            self.errors.append(f"Unexpected error: {str(e)}")

        return transactions

    def _parse_transaction(self, elem: ET.Element, trans_num: int) -> Dict[str, Any]:
        """
        Parse a single transaction XML element.

        Args:
            elem: XML element containing transaction data
            trans_num: Transaction number for error reporting

        Returns:
            Transaction dictionary or None if invalid
        """
        transaction = {}

        # Parse date (required)
        date_elem = elem.find('date')
        if date_elem is None or not date_elem.text:
            self.errors.append(f"Transaction {trans_num}: Date is required")
            return None

        transaction['date'] = self._parse_date(date_elem.text.strip(), trans_num)
        if not transaction['date']:
            return None

        # Parse description (required)
        desc_elem = elem.find('description')
        if desc_elem is None or not desc_elem.text:
            self.errors.append(f"Transaction {trans_num}: Description is required")
            return None
        transaction['description'] = desc_elem.text.strip()

        # Parse amount (required)
        amount_elem = elem.find('amount')
        if amount_elem is None or not amount_elem.text:
            self.errors.append(f"Transaction {trans_num}: Amount is required")
            return None

        transaction['amount'] = self._parse_amount(amount_elem.text.strip(), trans_num)
        if transaction['amount'] is None:
            return None

        # Parse category (required)
        category_elem = elem.find('category')
        if category_elem is None or not category_elem.text:
            self.errors.append(f"Transaction {trans_num}: Category is required")
            return None
        transaction['category'] = category_elem.text.strip()

        # Parse optional fields
        member_elem = elem.find('member')
        transaction['member'] = member_elem.text.strip() if member_elem is not None and member_elem.text else None

        source_elem = elem.find('source')
        transaction['source'] = source_elem.text.strip() if source_elem is not None and source_elem.text else None

        ref_elem = elem.find('reference_number')
        transaction['reference_number'] = ref_elem.text.strip() if ref_elem is not None and ref_elem.text else None

        return transaction

    def _parse_date(self, date_str: str, trans_num: int) -> datetime.date:
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

        self.errors.append(f"Transaction {trans_num}: Invalid date format '{date_str}'")
        return None

    def _parse_amount(self, amount_str: str, trans_num: int) -> Decimal:
        """Parse amount string into Decimal."""
        # Remove currency symbols and commas
        amount_str = amount_str.replace('$', '').replace(',', '').strip()

        try:
            amount = Decimal(amount_str)
            return amount
        except (InvalidOperation, ValueError):
            self.errors.append(f"Transaction {trans_num}: Invalid amount '{amount_str}'")
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
