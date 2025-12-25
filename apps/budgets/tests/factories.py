"""
Factory Boy factories for creating test instances of budget models.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal

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

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    """Factory for creating Category instances."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker("sentence")
    parent = None


class AccountingCategoryFactory(DjangoModelFactory):
    """Factory for creating AccountingCategory instances."""

    class Meta:
        model = AccountingCategory

    name = factory.Sequence(lambda n: f"Accounting Category {n}")
    description = factory.Faker("sentence")


class MemberFactory(DjangoModelFactory):
    """Factory for creating Member instances."""

    class Meta:
        model = Member

    name = factory.Sequence(lambda n: f"Member {n}")


class SourceFactory(DjangoModelFactory):
    """Factory for creating Source instances."""

    class Meta:
        model = Source

    name = factory.Sequence(lambda n: f"Source {n}")
    source_type = factory.Iterator(["income", "transfer", "other"])


class CategoryVendorFactory(DjangoModelFactory):
    """Factory for creating CategoryVendor instances."""

    class Meta:
        model = CategoryVendor

    name = factory.Sequence(lambda n: f"Vendor {n}")
    category = factory.SubFactory(CategoryFactory)
    irs_accounting_text = factory.Faker("sentence")


class BudgetGroupFactory(DjangoModelFactory):
    """Factory for creating BudgetGroup instances."""

    class Meta:
        model = BudgetGroup

    name = factory.Sequence(lambda n: f"Budget Group {n}")
    notes = factory.Faker("text", max_nb_chars=200)
    parent = None
    file_name_string = factory.LazyAttribute(lambda obj: f"/path/to/{obj.name}.budget")


class BudgetFactory(DjangoModelFactory):
    """Factory for creating Budget instances."""

    class Meta:
        model = Budget

    name = factory.Sequence(lambda n: f"Budget {n}")
    notes = factory.Faker("text", max_nb_chars=200)
    changes_made = False
    file_name_string = factory.LazyAttribute(lambda obj: f"/path/to/{obj.name}.budget")
    list_number = factory.Sequence(lambda n: n)
    current_sequence_number = 0
    is_copy = False
    is_whatif = False
    group = factory.SubFactory(BudgetGroupFactory)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        """Add categories to the budget after creation."""
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.add(category)
        else:
            # Add a default category
            self.categories.add(CategoryFactory())

    @factory.post_generation
    def accounting_categories(self, create, extracted, **kwargs):
        """Add accounting categories to the budget after creation."""
        if not create:
            return

        if extracted:
            for acc_cat in extracted:
                self.accounting_categories.add(acc_cat)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        """Add members to the budget after creation."""
        if not create:
            return

        if extracted:
            for member in extracted:
                self.members.add(member)

    @factory.post_generation
    def sources(self, create, extracted, **kwargs):
        """Add sources to the budget after creation."""
        if not create:
            return

        if extracted:
            for source in extracted:
                self.sources.add(source)


class BudgetItemFactory(DjangoModelFactory):
    """Factory for creating BudgetItem instances."""

    class Meta:
        model = BudgetItem

    unique_id = factory.Sequence(lambda n: f"ITEM-{n:06d}")
    sequence_number = factory.Sequence(lambda n: n)
    budget = factory.SubFactory(BudgetFactory)
    category = factory.SubFactory(CategoryFactory)
    monitary_value = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=False, min_value=-10000, max_value=10000
    )
    description = factory.Faker("sentence")
    date = factory.Faker("date_this_year")
    posted_date = factory.LazyAttribute(lambda obj: obj.date)
    short_date = factory.LazyAttribute(lambda obj: obj.date.strftime("%m/%d"))
    member = factory.SubFactory(MemberFactory)
    source = None
    category_vendor = None
    running_balance = Decimal("0.00")
    import_source = ""
    reference_number = ""
    imported = False
    marked = False
    is_breakout = False
    parent = None

    @factory.post_generation
    def accounting_categories(self, create, extracted, **kwargs):
        """Add accounting categories to the budget item after creation."""
        if not create:
            return

        if extracted:
            for acc_cat in extracted:
                self.accounting_categories.add(acc_cat)


class BudgetItemRelationFactory(DjangoModelFactory):
    """Factory for creating BudgetItemRelation instances."""

    class Meta:
        model = BudgetItemRelation

    item1 = factory.SubFactory(BudgetItemFactory)
    item2 = factory.SubFactory(BudgetItemFactory)
    relation_type = factory.Iterator(["linked", "transfer", "split_from", "correction"])
