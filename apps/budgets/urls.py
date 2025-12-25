"""
URL configuration for budgets app.
"""

from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('create/', views.budget_create, name='budget_create'),
    path('<uuid:pk>/', views.budget_detail, name='budget_detail'),
    path('<uuid:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('<uuid:pk>/delete/', views.budget_delete, name='budget_delete'),
    path('<uuid:pk>/copy/', views.budget_copy, name='budget_copy'),
    path('<uuid:pk>/whatif/', views.budget_whatif, name='budget_whatif'),
    path('<uuid:budget_id>/add-transaction/', views.add_transaction, name='add_transaction'),
    path('<uuid:budget_id>/bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('transaction/<uuid:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transaction/<uuid:pk>/delete/', views.delete_transaction, name='delete_transaction'),
]
