"""
Django admin configuration for import models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ImportTracker


@admin.register(ImportTracker)
class ImportTrackerAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'budget', 'items_imported', 'duplicates_found', 'get_success_rate', 'import_date']
    list_filter = ['file_type', 'budget', 'import_date']
    search_fields = ['file_name', 'source_name', 'notes']
    ordering = ['-import_date']
    readonly_fields = ['import_date', 'get_success_rate']
    autocomplete_fields = ['budget']

    fieldsets = (
        ('Import Information', {
            'fields': ('budget', 'file_name', 'file_type', 'source_name')
        }),
        ('Statistics', {
            'fields': ('items_imported', 'duplicates_found', 'get_success_rate', 'import_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def get_success_rate(self, obj):
        rate = obj.success_rate
        color = 'green' if rate >= 90 else 'orange' if rate >= 70 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    get_success_rate.short_description = 'Success Rate'
