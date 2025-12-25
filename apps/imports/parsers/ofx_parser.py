"""
OFX parser for importing bank transactions from OFX/QFX files.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any
from io import StringIO
import ofxparse


class OFXParser:
    """Parse OFX/QFX files to extract budget transaction data."""

    def __init__(self, file_content: str):
        """
        Initialize the OFX parser.

        Args:
            file_content: The OFX file content as a string
        """
        self.file_content = file_content
        self.errors = []
        self.warnings = []

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse the OFX content and return a list of transaction dictionaries.

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        try:
            # Parse OFX file
            ofx = ofxparse.OfxParser.parse(StringIO(self.file_content))

            # Check if we have any accounts
            if not hasattr(ofx, 'account') or not ofx.account:
                self.errors.append("No account information found in OFX file")
                return []

            account = ofx.account

            # Check if we have a statement
            if not hasattr(account, 'statement') or not account.statement:
                self.errors.append("No statement information found in OFX file")
                return []

            statement = account.statement

            # Get transactions from statement
            if not hasattr(statement, 'transactions') or not statement.transactions:
                self.warnings.append("No transactions found in statement")
                return []

            # Parse each transaction
            for idx, ofx_transaction in enumerate(statement.transactions, start=1):
                try:
                    transaction = self._parse_transaction(ofx_transaction, idx)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    self.errors.append(f"Transaction {idx}: {str(e)}")

        except ofxparse.OfxParserException as e:
            self.errors.append(f"OFX parsing error: {str(e)}")
        except Exception as e:
            self.errors.append(f"Unexpected error: {str(e)}")

        return transactions

    def _parse_transaction(self, ofx_trans, trans_num: int) -> Dict[str, Any]:
        """
        Parse a single OFX transaction.

        Args:
            ofx_trans: OFX transaction object from ofxparse
            trans_num: Transaction number for error reporting

        Returns:
            Transaction dictionary or None if invalid
        """
        transaction = {}

        # Parse date (required)
        if not hasattr(ofx_trans, 'date') or not ofx_trans.date:
            self.errors.append(f"Transaction {trans_num}: Date is required")
            return None

        transaction['date'] = ofx_trans.date.date() if hasattr(ofx_trans.date, 'date') else ofx_trans.date

        # Parse amount (required)
        if not hasattr(ofx_trans, 'amount') or ofx_trans.amount is None:
            self.errors.append(f"Transaction {trans_num}: Amount is required")
            return None

        try:
            transaction['amount'] = Decimal(str(ofx_trans.amount))
        except (InvalidOperation, ValueError):
            self.errors.append(f"Transaction {trans_num}: Invalid amount '{ofx_trans.amount}'")
            return None

        # Build description from available fields
        description_parts = []

        # Add payee/merchant name
        if hasattr(ofx_trans, 'payee') and ofx_trans.payee:
            description_parts.append(str(ofx_trans.payee).strip())

        # Add memo if available
        if hasattr(ofx_trans, 'memo') and ofx_trans.memo:
            memo = str(ofx_trans.memo).strip()
            # Only add memo if it's different from payee
            if not description_parts or memo not in description_parts[0]:
                description_parts.append(memo)

        # Fallback to type if no description
        if not description_parts:
            if hasattr(ofx_trans, 'type') and ofx_trans.type:
                description_parts.append(str(ofx_trans.type))

        transaction['description'] = ' - '.join(description_parts) if description_parts else 'Transaction'

        # Determine category based on transaction type and amount
        category = self._determine_category(ofx_trans)
        transaction['category'] = category

        # Parse reference number/ID
        if hasattr(ofx_trans, 'id') and ofx_trans.id:
            transaction['reference_number'] = str(ofx_trans.id)
        elif hasattr(ofx_trans, 'checknum') and ofx_trans.checknum:
            transaction['reference_number'] = f"CHECK-{ofx_trans.checknum}"
        else:
            transaction['reference_number'] = ''

        # Optional: member field (can be left None)
        transaction['member'] = None

        # Optional: source field (bank account name if available)
        transaction['source'] = None

        return transaction

    def _determine_category(self, ofx_trans) -> str:
        """
        Determine category based on transaction type and description.

        Args:
            ofx_trans: OFX transaction object

        Returns:
            Category name
        """
        # Get transaction type
        trans_type = None
        if hasattr(ofx_trans, 'type') and ofx_trans.type:
            trans_type = str(ofx_trans.type).upper()

        # Get amount
        amount = Decimal(str(ofx_trans.amount)) if hasattr(ofx_trans, 'amount') else Decimal('0')

        # Categorize based on type
        if trans_type == 'CHECK':
            return 'Check'
        elif trans_type == 'DEBIT' or amount < 0:
            # Try to categorize based on description
            description = self._get_description_text(ofx_trans).upper()

            if any(word in description for word in ['GROCERY', 'KROGER', 'WALMART', 'TARGET']):
                return 'Groceries'
            elif any(word in description for word in ['RESTAURANT', 'FOOD', 'CAFE', 'MCDONALD', 'BURGER', 'PIZZA']):
                return 'Food & Dining'
            elif any(word in description for word in ['GAS', 'FUEL', 'EXXON', 'SHELL', 'CHEVRON', 'MOBIL']):
                return 'Gas & Fuel'
            elif any(word in description for word in ['PHARMACY', 'CVS', 'WALGREEN', 'MEDICAL', 'DOCTOR', 'HOSPITAL']):
                return 'Healthcare'
            elif any(word in description for word in ['ELECTRIC', 'WATER', 'GAS', 'UTILITY', 'COMCAST', 'AT&T', 'PHONE']):
                return 'Utilities'
            elif any(word in description for word in ['AMAZON', 'EBAY', 'SHOPPING']):
                return 'Shopping'
            else:
                return 'Expenses'
        elif trans_type == 'CREDIT' or amount > 0:
            description = self._get_description_text(ofx_trans).upper()
            if 'DEPOSIT' in description or 'PAYCHECK' in description or 'SALARY' in description:
                return 'Income'
            elif 'PAYMENT' in description or 'AUTOPAY' in description:
                return 'Payment'
            else:
                return 'Income'
        else:
            # Default to Expenses for negative, Income for positive
            return 'Expenses' if amount < 0 else 'Income'

    def _get_description_text(self, ofx_trans) -> str:
        """Get combined description text from transaction."""
        parts = []
        if hasattr(ofx_trans, 'payee') and ofx_trans.payee:
            parts.append(str(ofx_trans.payee))
        if hasattr(ofx_trans, 'memo') and ofx_trans.memo:
            parts.append(str(ofx_trans.memo))
        return ' '.join(parts)

    def has_errors(self) -> bool:
        """Check if any errors occurred during parsing."""
        return len(self.errors) > 0

    def get_errors(self) -> List[str]:
        """Get list of all parsing errors."""
        return self.errors

    def get_warnings(self) -> List[str]:
        """Get list of all parsing warnings."""
        return self.warnings
