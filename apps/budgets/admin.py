"""
Django admin configuration for budget models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'description']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(AccountingCategory)
class AccountingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type']
    list_filter = ['source_type']
    search_fields = ['name']
    ordering = ['name']


@admin.register(CategoryVendor)
class CategoryVendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'irs_accounting_text']
    list_filter = ['category']
    search_fields = ['name', 'irs_accounting_text']
    ordering = ['name']
    autocomplete_fields = ['category']


@admin.register(BudgetGroup)
class BudgetGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'get_full_path', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'notes']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def get_full_path(self, obj):
        return obj.get_full_path()
    get_full_path.short_description = 'Full Path'


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 0
    fields = ['date', 'description', 'category', 'monitary_value', 'member', 'running_balance']
    readonly_fields = ['running_balance', 'unique_id']
    autocomplete_fields = ['category', 'member', 'source']
    show_change_link = True


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'is_copy', 'is_whatif', 'get_item_count', 'get_balance', 'created_at']
    list_filter = ['group', 'is_copy', 'is_whatif', 'created_at']
    search_fields = ['name', 'notes']
    ordering = ['-created_at', 'name']
    readonly_fields = ['created_at', 'updated_at', 'current_sequence_number', 'get_item_count', 'get_balance']
    filter_horizontal = ['categories', 'accounting_categories', 'members', 'sources']
    inlines = [BudgetItemInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'group', 'notes')
        }),
        ('Settings', {
            'fields': ('is_copy', 'is_whatif', 'changes_made', 'current_sequence_number')
        }),
        ('Filters', {
            'fields': ('categories', 'accounting_categories', 'members', 'sources'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'file_name_string', 'list_number'),
            'classes': ('collapse',)
        }),
    )

    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'

    def get_balance(self, obj):
        balance = obj.get_current_balance()
        color = 'green' if balance >= 0 else 'red'
        return format_html('<span style="color: {};">${:,.2f}</span>', color, balance)
    get_balance.short_description = 'Balance'


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'category', 'get_amount', 'member', 'budget', 'running_balance', 'imported']
    list_filter = ['budget', 'category', 'member', 'source', 'imported', 'is_breakout', 'date']
    search_fields = ['description', 'unique_id', 'reference_number']
    ordering = ['-date', '-sequence_number']
    readonly_fields = ['unique_id', 'sequence_number', 'running_balance', 'update_timestamp', 'created_at', 'updated_at']
    autocomplete_fields = ['budget', 'category', 'member', 'source', 'category_vendor', 'parent']
    date_hierarchy = 'date'

    fieldsets = (
        ('Transaction Details', {
            'fields': ('budget', 'date', 'description', 'monitary_value', 'category')
        }),
        ('Additional Information', {
            'fields': ('member', 'source', 'category_vendor', 'posted_date', 'short_date', 'reference_number')
        }),
        ('Accounting', {
            'fields': ('accounting_categories', 'running_balance'),
            'classes': ('collapse',)
        }),
        ('Import & State', {
            'fields': ('imported', 'import_source', 'marked', 'is_breakout', 'parent'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('unique_id', 'sequence_number', 'update_timestamp', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_amount(self, obj):
        color = 'green' if obj.monitary_value >= 0 else 'red'
        symbol = '+' if obj.monitary_value >= 0 else ''
        return format_html('<span style="color: {};">{}{:,.2f}</span>', color, symbol, obj.monitary_value)
    get_amount.short_description = 'Amount'


@admin.register(BudgetItemRelation)
class BudgetItemRelationAdmin(admin.ModelAdmin):
    list_display = ['item1', 'relation_type', 'item2']
    list_filter = ['relation_type']
    search_fields = ['item1__description', 'item2__description', 'notes']
    autocomplete_fields = ['item1', 'item2']
