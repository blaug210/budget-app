"""
Unit tests for budget models.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from apps.budgets.models import (
    Category,
    AccountingCategory,
    Member,
    Source,
    CategoryVendor,
    BudgetGroup,
    Budget,
    BudgetItem,
    BudgetItemRelation,
)
from .factories import (
    CategoryFactory,
    AccountingCategoryFactory,
    MemberFactory,
    SourceFactory,
    CategoryVendorFactory,
    BudgetGroupFactory,
    BudgetFactory,
    BudgetItemFactory,
    BudgetItemRelationFactory,
)


@pytest.mark.django_db
class TestCategory:
    """Tests for the Category model."""

    def test_create_category(self):
        """Test creating a category."""
        category = CategoryFactory(name="Groceries")
        assert category.name == "Groceries"
        assert category.description is not None
        assert str(category) == "Groceries"

    def test_category_unique_name(self):
        """Test that category names must be unique."""
        CategoryFactory(name="Groceries")
        with pytest.raises(IntegrityError):
            CategoryFactory(name="Groceries")

    def test_category_hierarchy(self):
        """Test category parent-child relationship."""
        parent = CategoryFactory(name="Food")
        child = CategoryFactory(name="Groceries", parent=parent)
        assert child.parent == parent
        assert child in parent.subcategories.all()

    def test_category_ordering(self):
        """Test categories are ordered by name."""
        CategoryFactory(name="Zebra")
        CategoryFactory(name="Apple")
        categories = Category.objects.all()
        assert categories[0].name == "Apple"
        assert categories[1].name == "Zebra"


@pytest.mark.django_db
class TestAccountingCategory:
    """Tests for the AccountingCategory model."""

    def test_create_accounting_category(self):
        """Test creating an accounting category."""
        acc_cat = AccountingCategoryFactory(name="Business Expenses")
        assert acc_cat.name == "Business Expenses"
        assert str(acc_cat) == "Business Expenses"

    def test_accounting_category_unique_name(self):
        """Test that accounting category names must be unique."""
        AccountingCategoryFactory(name="Business Expenses")
        with pytest.raises(IntegrityError):
            AccountingCategoryFactory(name="Business Expenses")


@pytest.mark.django_db
class TestMember:
    """Tests for the Member model."""

    def test_create_member(self):
        """Test creating a member."""
        member = MemberFactory(name="John Doe")
        assert member.name == "John Doe"
        assert str(member) == "John Doe"

    def test_member_unique_name(self):
        """Test that member names must be unique."""
        MemberFactory(name="John Doe")
        with pytest.raises(IntegrityError):
            MemberFactory(name="John Doe")


@pytest.mark.django_db
class TestSource:
    """Tests for the Source model."""

    def test_create_source(self):
        """Test creating a source."""
        source = SourceFactory(name="Salary", source_type="income")
        assert source.name == "Salary"
        assert source.source_type == "income"
        assert str(source) == "Salary (Income)"

    def test_source_unique_name(self):
        """Test that source names must be unique."""
        SourceFactory(name="Salary")
        with pytest.raises(IntegrityError):
            SourceFactory(name="Salary")

    def test_source_types(self):
        """Test different source types."""
        for source_type in ["income", "transfer", "other"]:
            source = SourceFactory(source_type=source_type)
            assert source.source_type == source_type


@pytest.mark.django_db
class TestCategoryVendor:
    """Tests for the CategoryVendor model."""

    def test_create_category_vendor(self):
        """Test creating a category vendor."""
        category = CategoryFactory(name="Shopping")
        vendor = CategoryVendorFactory(
            name="Walmart", category=category, irs_accounting_text="Retail purchases"
        )
        assert vendor.name == "Walmart"
        assert vendor.category == category
        assert vendor.irs_accounting_text == "Retail purchases"
        assert str(vendor) == "Walmart (Shopping)"

    def test_vendor_unique_name(self):
        """Test that vendor names must be unique."""
        CategoryVendorFactory(name="Walmart")
        with pytest.raises(IntegrityError):
            CategoryVendorFactory(name="Walmart")


@pytest.mark.django_db
class TestBudgetGroup:
    """Tests for the BudgetGroup model."""

    def test_create_budget_group(self):
        """Test creating a budget group."""
        group = BudgetGroupFactory(name="2024 Budgets")
        assert group.name == "2024 Budgets"
        assert group.notes is not None
        assert str(group) == "2024 Budgets"

    def test_budget_group_hierarchy(self):
        """Test budget group parent-child relationship."""
        parent = BudgetGroupFactory(name="2024")
        child = BudgetGroupFactory(name="January", parent=parent)
        assert child.parent == parent
        assert child in parent.children.all()

    def test_budget_group_get_full_path(self):
        """Test getting full path of nested groups."""
        parent = BudgetGroupFactory(name="2024")
        child = BudgetGroupFactory(name="Q1", parent=parent)
        grandchild = BudgetGroupFactory(name="January", parent=child)

        assert grandchild.get_full_path() == "2024 / Q1 / January"


@pytest.mark.django_db
class TestBudget:
    """Tests for the Budget model."""

    def test_create_budget(self):
        """Test creating a budget."""
        budget = BudgetFactory(name="Monthly Budget")
        assert budget.name == "Monthly Budget"
        assert budget.current_sequence_number == 0
        assert not budget.is_copy
        assert not budget.is_whatif
        assert str(budget) == "Monthly Budget"

    def test_budget_relationships(self):
        """Test budget many-to-many relationships."""
        category = CategoryFactory()
        member = MemberFactory()
        budget = BudgetFactory(categories=[category], members=[member])

        assert category in budget.categories.all()
        assert member in budget.members.all()

    def test_budget_get_next_sequence_number(self):
        """Test getting and incrementing sequence number."""
        budget = BudgetFactory(current_sequence_number=0)
        assert budget.get_next_sequence_number() == 1
        assert budget.current_sequence_number == 1

        assert budget.get_next_sequence_number() == 2
        assert budget.current_sequence_number == 2

    def test_budget_get_date_range(self):
        """Test getting date range of budget items."""
        budget = BudgetFactory()
        today = date.today()

        # Budget with no items
        date_range = budget.get_date_range()
        assert date_range == (None, None)

        # Add items with different dates
        BudgetItemFactory(budget=budget, date=today - timedelta(days=10))
        BudgetItemFactory(budget=budget, date=today)
        BudgetItemFactory(budget=budget, date=today + timedelta(days=5))

        date_range = budget.get_date_range()
        assert date_range[0] == today - timedelta(days=10)
        assert date_range[1] == today + timedelta(days=5)


@pytest.mark.django_db
class TestBudgetItem:
    """Tests for the BudgetItem model."""

    def test_create_budget_item(self):
        """Test creating a budget item."""
        item = BudgetItemFactory(
            monitary_value=Decimal("-100.50"),
            description="Grocery shopping",
        )
        assert item.monitary_value == Decimal("-100.50")
        assert item.description == "Grocery shopping"
        assert item.unique_id is not None
        assert str(item) == f"{item.date} - Grocery shopping ($-100.50)"

    def test_budget_item_unique_id_generation(self):
        """Test that unique_id is unique."""
        item1 = BudgetItemFactory()
        item2 = BudgetItemFactory()
        assert item1.unique_id != item2.unique_id

    def test_budget_item_sequence_number(self):
        """Test sequence number auto-increment."""
        budget = BudgetFactory()
        item1 = BudgetItemFactory(budget=budget, sequence_number=1)
        item2 = BudgetItemFactory(budget=budget, sequence_number=2)

        assert item1.sequence_number == 1
        assert item2.sequence_number == 2

    def test_budget_item_is_income(self):
        """Test is_income property."""
        income = BudgetItemFactory(monitary_value=Decimal("100.00"))
        expense = BudgetItemFactory(monitary_value=Decimal("-100.00"))

        assert income.is_income is True
        assert expense.is_income is False

    def test_budget_item_is_expense(self):
        """Test is_expense property."""
        income = BudgetItemFactory(monitary_value=Decimal("100.00"))
        expense = BudgetItemFactory(monitary_value=Decimal("-100.00"))

        assert income.is_expense is False
        assert expense.is_expense is True

    def test_budget_item_breakout(self):
        """Test breakout parent-child relationship."""
        parent = BudgetItemFactory(monitary_value=Decimal("-100.00"))
        child1 = BudgetItemFactory(
            budget=parent.budget,
            parent=parent,
            is_breakout=True,
            monitary_value=Decimal("-60.00"),
        )
        child2 = BudgetItemFactory(
            budget=parent.budget,
            parent=parent,
            is_breakout=True,
            monitary_value=Decimal("-40.00"),
        )

        assert child1.parent == parent
        assert child2.parent == parent
        assert child1 in parent.breakouts.all()
        assert child2 in parent.breakouts.all()
        assert parent.breakouts.count() == 2

    def test_budget_item_ordering(self):
        """Test budget items are ordered by date and sequence."""
        budget = BudgetFactory()
        today = date.today()

        item3 = BudgetItemFactory(budget=budget, date=today, sequence_number=2)
        item1 = BudgetItemFactory(budget=budget, date=today - timedelta(days=1), sequence_number=1)
        item2 = BudgetItemFactory(budget=budget, date=today, sequence_number=1)

        items = BudgetItem.objects.filter(budget=budget)
        assert list(items) == [item1, item2, item3]


@pytest.mark.django_db
class TestBudgetItemRelation:
    """Tests for the BudgetItemRelation model."""

    def test_create_relation(self):
        """Test creating a budget item relation."""
        item1 = BudgetItemFactory(description="Expense")
        item2 = BudgetItemFactory(description="Income")
        relation = BudgetItemRelationFactory(
            item1=item1, item2=item2, relation_type="linked"
        )

        assert relation.item1 == item1
        assert relation.item2 == item2
        assert relation.relation_type == "linked"
        assert str(relation) == "Expense Linked Income"

    def test_relation_types(self):
        """Test different relation types."""
        for rel_type in ["linked", "transfer", "split_from", "correction"]:
            relation = BudgetItemRelationFactory(relation_type=rel_type)
            assert relation.relation_type == rel_type

    @pytest.mark.django_db(transaction=True)
    def test_relation_unique_together(self):
        """Test that item1+item2+relation_type must be unique."""
        from django.db import transaction

        item1 = BudgetItemFactory()
        item2 = BudgetItemFactory()
        BudgetItemRelationFactory(item1=item1, item2=item2, relation_type="linked")

        # Should fail: same items, same relation type
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                BudgetItemRelationFactory(item1=item1, item2=item2, relation_type="linked")

        # Should succeed: same items, different relation type
        BudgetItemRelationFactory(item1=item1, item2=item2, relation_type="transfer")
