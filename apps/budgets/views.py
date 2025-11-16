"""
Views for budgets app.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Budget, BudgetItem, Category, Member, Source


def budget_list(request):
    """Display list of all budgets with summary information."""
    budgets = Budget.objects.select_related('group').annotate(
        item_count=Count('items'),
        total_balance=Sum('items__monitary_value')
    ).order_by('-created_at')

    context = {
        'budgets': budgets,
    }
    return render(request, 'budgets/budget_list.html', context)


def budget_detail(request, pk):
    """Display budget detail with all transactions."""
    budget = get_object_or_404(
        Budget.objects.select_related('group').prefetch_related(
            'items__category',
            'items__member',
            'items__source'
        ),
        pk=pk
    )

    # Get all items ordered by date and sequence
    items = budget.items.all().order_by('-date', '-sequence_number')

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
            category_id = request.POST.get('category')
            member_id = request.POST.get('member')
            source_id = request.POST.get('source')

            # Create the transaction
            item = BudgetItem(
                budget=budget,
                date=date,
                description=description,
                monitary_value=amount,
                category_id=category_id,
            )

            # Add optional fields
            if member_id:
                item.member_id = member_id
            if source_id:
                item.source_id = source_id

            item.save()

            messages.success(request, f'Transaction "{description}" added successfully!')

        except Exception as e:
            messages.error(request, f'Error adding transaction: {str(e)}')

    return redirect('budgets:budget_detail', pk=budget_id)
