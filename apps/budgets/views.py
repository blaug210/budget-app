"""
Views for budgets app.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Budget, BudgetItem, Category, Member, Source, BudgetGroup
from apps.imports.parsers.csv_parser import CSVParser
from apps.imports.parsers.xml_parser import XMLParser
from apps.imports.parsers.ofx_parser import OFXParser
from apps.imports.services.import_service import ImportService


def budget_list(request):
    """Display list of all budgets with summary information."""
    from django.db.models import Q, Case, When, Value, DecimalField
    from decimal import Decimal

    budgets = Budget.objects.select_related('group').annotate(
        item_count=Count('items'),
        # Exclude beginning balances from total balance calculation
        total_balance=Sum(
            Case(
                When(
                    Q(items__description__icontains='beginning balance') |
                    Q(items__description__icontains='begin balance'),
                    then=Value(Decimal('0'))
                ),
                default='items__monitary_value',
                output_field=DecimalField()
            )
        )
    ).order_by('-created_at')

    context = {
        'budgets': budgets,
    }
    return render(request, 'budgets/budget_list.html', context)


def budget_create(request):
    """Create a new budget."""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            group_id = request.POST.get('group')
            notes = request.POST.get('notes', '')
            is_copy = request.POST.get('is_copy') == 'on'
            is_whatif = request.POST.get('is_whatif') == 'on'

            # Validate required fields
            if not name:
                messages.error(request, 'Budget name is required.')
                return redirect('budgets:budget_create')

            # Get or create budget group
            if group_id:
                group = get_object_or_404(BudgetGroup, pk=group_id)
            else:
                # Create a default group if none selected
                group, _ = BudgetGroup.objects.get_or_create(
                    name='Default',
                    defaults={'file_name_string': '/budgets/default'}
                )

            # Create the budget
            budget = Budget.objects.create(
                name=name,
                group=group,
                notes=notes,
                is_copy=is_copy,
                is_whatif=is_whatif,
                file_name_string=f'/budgets/{group.name.lower()}/{name.lower().replace(" ", "_")}'
            )

            messages.success(request, f'Budget "{name}" created successfully!')
            return redirect('budgets:budget_detail', pk=budget.pk)

        except Exception as e:
            messages.error(request, f'Error creating budget: {str(e)}')
            return redirect('budgets:budget_create')

    # GET request - show form
    groups = BudgetGroup.objects.all().order_by('name')
    context = {
        'groups': groups,
    }
    return render(request, 'budgets/budget_form.html', context)


def budget_edit(request, pk):
    """Edit an existing budget."""
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        try:
            # Update budget fields
            budget.name = request.POST.get('name')
            group_id = request.POST.get('group')

            if group_id:
                budget.group = get_object_or_404(BudgetGroup, pk=group_id)

            budget.notes = request.POST.get('notes', '')
            budget.is_copy = request.POST.get('is_copy') == 'on'
            budget.is_whatif = request.POST.get('is_whatif') == 'on'

            budget.save()

            messages.success(request, f'Budget "{budget.name}" updated successfully!')
            return redirect('budgets:budget_detail', pk=budget.pk)

        except Exception as e:
            messages.error(request, f'Error updating budget: {str(e)}')
            return redirect('budgets:budget_edit', pk=pk)

    # GET request - show form
    groups = BudgetGroup.objects.all().order_by('name')
    context = {
        'budget': budget,
        'groups': groups,
        'is_edit': True,
    }
    return render(request, 'budgets/budget_form.html', context)


def budget_delete(request, pk):
    """Delete a budget."""
    budget = get_object_or_404(Budget, pk=pk)
    budget_name = budget.name

    if request.method == 'POST':
        try:
            budget.delete()
            messages.success(request, f'Budget "{budget_name}" deleted successfully!')
            return redirect('budgets:budget_list')
        except Exception as e:
            messages.error(request, f'Error deleting budget: {str(e)}')
            return redirect('budgets:budget_detail', pk=pk)

    # GET request - show confirmation
    context = {'budget': budget}
    return render(request, 'budgets/budget_confirm_delete.html', context)


def budget_copy(request, pk):
    """Create a copy of an existing budget."""
    source_budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        try:
            # Get the new budget name
            new_name = request.POST.get('name')
            if not new_name:
                new_name = f"{source_budget.name} - Copy"

            # Create the copy
            budget_copy = Budget.objects.create(
                name=new_name,
                group=source_budget.group,
                notes=source_budget.notes,
                is_copy=True,  # Mark as a copy
                is_whatif=False,
                file_name_string=f'/budgets/{source_budget.group.name.lower()}/{new_name.lower().replace(" ", "_")}'
            )

            # Copy all budget items
            items_to_copy = source_budget.items.all()
            for item in items_to_copy:
                new_item = BudgetItem.objects.create(
                    budget=budget_copy,
                    date=item.date,
                    description=item.description,
                    monitary_value=item.monitary_value,
                    member=item.member,
                    source=item.source,
                    category_vendor=item.category_vendor,
                    reference_number=item.reference_number,
                    imported=item.imported,
                    import_source=item.import_source,
                    marked=item.marked,
                    posted_date=item.posted_date,
                    short_date=item.short_date,
                )
                # Copy categories (must be done after save for M2M)
                new_item.categories.set(item.categories.all())

            messages.success(request, f'Budget copied successfully as "{new_name}" with {items_to_copy.count()} transactions!')
            return redirect('budgets:budget_detail', pk=budget_copy.pk)

        except Exception as e:
            messages.error(request, f'Error copying budget: {str(e)}')
            return redirect('budgets:budget_detail', pk=pk)

    # GET request - show confirmation form
    context = {
        'budget': source_budget,
        'action': 'copy',
    }
    return render(request, 'budgets/budget_copy.html', context)


def budget_whatif(request, pk):
    """Create a what-if scenario based on an existing budget."""
    source_budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        try:
            # Get the new scenario name
            new_name = request.POST.get('name')
            if not new_name:
                new_name = f"{source_budget.name} - What-If"

            # Create the what-if scenario
            whatif_budget = Budget.objects.create(
                name=new_name,
                group=source_budget.group,
                notes=source_budget.notes,
                is_copy=False,
                is_whatif=True,  # Mark as what-if scenario
                file_name_string=f'/budgets/{source_budget.group.name.lower()}/{new_name.lower().replace(" ", "_")}'
            )

            # Copy all budget items
            items_to_copy = source_budget.items.all()
            for item in items_to_copy:
                new_item = BudgetItem.objects.create(
                    budget=whatif_budget,
                    date=item.date,
                    description=item.description,
                    monitary_value=item.monitary_value,
                    member=item.member,
                    source=item.source,
                    category_vendor=item.category_vendor,
                    reference_number=item.reference_number,
                    imported=item.imported,
                    import_source=item.import_source,
                    marked=item.marked,
                    posted_date=item.posted_date,
                    short_date=item.short_date,
                )
                # Copy categories (must be done after save for M2M)
                new_item.categories.set(item.categories.all())

            messages.success(request, f'What-If scenario "{new_name}" created with {items_to_copy.count()} transactions! You can now modify it for planning.')
            return redirect('budgets:budget_detail', pk=whatif_budget.pk)

        except Exception as e:
            messages.error(request, f'Error creating what-if scenario: {str(e)}')
            return redirect('budgets:budget_detail', pk=pk)

    # GET request - show confirmation form
    context = {
        'budget': source_budget,
        'action': 'whatif',
    }
    return render(request, 'budgets/budget_copy.html', context)


def budget_detail(request, pk):
    """Display budget detail with paginated transactions."""
    budget = get_object_or_404(
        Budget.objects.select_related('group'),
        pk=pk
    )

    # Get all items ordered by date and sequence
    items_list = budget.items.select_related('member', 'source').prefetch_related('categories').order_by('-date', '-sequence_number')

    # Pagination - 100 items per page
    page = request.GET.get('page', 1)
    paginator = Paginator(items_list, 100)

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    # Get categories, members, and sources for the form
    categories = Category.objects.all().order_by('name')
    members = Member.objects.all().order_by('name')
    sources = Source.objects.all().order_by('name')

    # Calculate totals
    income_total = budget.get_total_income()
    expense_total = budget.get_total_expenses()
    current_balance = budget.get_current_balance()

    context = {
        'budget': budget,
        'items': items,
        'categories': categories,
        'members': members,
        'sources': sources,
        'income_total': income_total,
        'expense_total': expense_total,
        'current_balance': current_balance,
    }
    return render(request, 'budgets/budget_detail.html', context)


def add_transaction(request, budget_id):
    """Add a new transaction to a budget."""
    budget = get_object_or_404(Budget, pk=budget_id)

    if request.method == 'POST':
        try:
            # Get form data
            date = request.POST.get('date')
            description = request.POST.get('description')
            amount = request.POST.get('amount')
            category_ids = request.POST.getlist('categories')  # Get multiple categories
            member_id = request.POST.get('member')
            source_id = request.POST.get('source')

            # Create the transaction
            item = BudgetItem(
                budget=budget,
                date=date,
                description=description,
                monitary_value=amount,
            )

            # Add optional fields
            if member_id:
                item.member_id = member_id
            if source_id:
                item.source_id = source_id

            item.save()

            # Add categories (must be done after save for M2M)
            if category_ids:
                item.categories.set(category_ids)

            messages.success(request, f'Transaction "{description}" added successfully!')

        except Exception as e:
            messages.error(request, f'Error adding transaction: {str(e)}')

    return redirect('budgets:budget_detail', pk=budget_id)


def edit_transaction(request, pk):
    """Edit an existing transaction."""
    item = get_object_or_404(BudgetItem, pk=pk)
    budget = item.budget

    if request.method == 'POST':
        try:
            # Update transaction fields
            item.date = request.POST.get('date')
            item.description = request.POST.get('description')
            item.monitary_value = request.POST.get('amount')

            # Update categories
            category_ids = request.POST.getlist('categories')
            if category_ids:
                item.categories.set(category_ids)

            # Update optional fields
            member_id = request.POST.get('member')
            item.member_id = member_id if member_id else None

            source_id = request.POST.get('source')
            item.source_id = source_id if source_id else None

            item.save()

            messages.success(request, f'Transaction "{item.description}" updated successfully!')

        except Exception as e:
            messages.error(request, f'Error updating transaction: {str(e)}')

    return redirect('budgets:budget_detail', pk=budget.pk)


def delete_transaction(request, pk):
    """Delete a transaction."""
    item = get_object_or_404(BudgetItem, pk=pk)
    budget = item.budget
    description = item.description

    if request.method == 'POST':
        try:
            item.delete()
            messages.success(request, f'Transaction "{description}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting transaction: {str(e)}')

    return redirect('budgets:budget_detail', pk=budget.pk)


def bulk_upload(request, budget_id):
    """Handle bulk upload of transactions from CSV, XML, or OFX files."""
    budget = get_object_or_404(Budget, pk=budget_id)

    if request.method == 'POST':
        try:
            # Get uploaded file
            uploaded_file = request.FILES.get('file')
            file_type = request.POST.get('file_type', 'csv')

            if not uploaded_file:
                messages.error(request, 'No file was uploaded.')
                return redirect('budgets:budget_detail', pk=budget_id)

            # Read file content
            file_content = uploaded_file.read().decode('utf-8')

            # Parse file based on type
            if file_type == 'csv':
                parser = CSVParser(file_content)
            elif file_type == 'xml':
                parser = XMLParser(file_content)
            elif file_type == 'ofx':
                parser = OFXParser(file_content)
            else:
                messages.error(request, f'Unsupported file type: {file_type}')
                return redirect('budgets:budget_detail', pk=budget_id)

            # Parse the file
            transactions = parser.parse()

            # Check for parsing errors
            if parser.has_errors():
                error_msg = f'File parsing errors:<br><ul>'
                for error in parser.get_errors()[:5]:  # Show first 5 errors
                    error_msg += f'<li>{error}</li>'
                if len(parser.get_errors()) > 5:
                    error_msg += f'<li>... and {len(parser.get_errors()) - 5} more errors</li>'
                error_msg += '</ul>'
                messages.error(request, error_msg, extra_tags='safe')
                return redirect('budgets:budget_detail', pk=budget_id)

            if not transactions:
                messages.warning(request, 'No valid transactions found in the file.')
                return redirect('budgets:budget_detail', pk=budget_id)

            # Import transactions
            import_service = ImportService(budget)
            result = import_service.import_transactions(
                transactions,
                uploaded_file.name,
                file_type
            )

            # Display results
            stats = result['stats']
            success_msg = f'<strong>Import Complete!</strong><br>'
            success_msg += f'✅ Imported: {stats["imported"]} transactions<br>'

            if stats['duplicates'] > 0:
                success_msg += f'⚠️ Duplicates skipped: {stats["duplicates"]}<br>'

            if stats['errors'] > 0:
                success_msg += f'❌ Errors: {stats["errors"]}<br>'
                if result['errors']:
                    success_msg += '<br><strong>Errors:</strong><ul>'
                    for error in result['errors'][:5]:
                        success_msg += f'<li>{error}</li>'
                    if len(result['errors']) > 5:
                        success_msg += f'<li>... and {len(result["errors"]) - 5} more errors</li>'
                    success_msg += '</ul>'

            if stats['imported'] > 0:
                messages.success(request, success_msg, extra_tags='safe')
            else:
                messages.warning(request, success_msg, extra_tags='safe')

        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')

    return redirect('budgets:budget_detail', pk=budget_id)
