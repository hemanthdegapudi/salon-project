from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_entry, name='customer_entry'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('income-detail/', views.income_detail, name='income_detail'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('monthly-income-detail/', views.monthly_income_detail, name='monthly_income_detail'),
]