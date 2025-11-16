"""
URL configuration for budgets app.
"""

from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('<uuid:pk>/', views.budget_detail, name='budget_detail'),
    path('<uuid:budget_id>/add-transaction/', views.add_transaction, name='add_transaction'),
    path('transaction/<uuid:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transaction/<uuid:pk>/delete/', views.delete_transaction, name='delete_transaction'),
]
