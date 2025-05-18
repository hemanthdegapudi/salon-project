from django.shortcuts import render, redirect
from .models import ServiceRecord, InventoryItem, Staff, FinancialRecord
from django.db.models import Sum
from django.db import models
from datetime import date, timedelta
from django import forms
from django.db.models.functions import TruncDate

def dashboard(request):
    today = date.today()
    week_ago = today - timedelta(days=6)
    month_ago = today.replace(day=1)

    today_income = FinancialRecord.objects.filter(record_type='income', date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    today_expense = FinancialRecord.objects.filter(record_type='expense', date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    week_income = FinancialRecord.objects.filter(record_type='income', date__gte=week_ago).aggregate(Sum('amount'))['amount__sum'] or 0
    month_income = FinancialRecord.objects.filter(record_type='income', date__gte=month_ago).aggregate(Sum('amount'))['amount__sum'] or 0

    today_services = ServiceRecord.objects.filter(date__date=today).count()
    staff_count = Staff.objects.count()
    low_inventory = InventoryItem.objects.filter(quantity__lte=models.F('threshold')).count()

    labels = []
    income_data = []
    expense_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%a'))
        income = FinancialRecord.objects.filter(record_type='income', date=day).aggregate(Sum('amount'))['amount__sum'] or 0
        expense = FinancialRecord.objects.filter(record_type='expense', date=day).aggregate(Sum('amount'))['amount__sum'] or 0
        income_data.append(float(income))
        expense_data.append(float(expense))

    context = {
        'today_income': today_income,
        'today_expense': today_expense,
        'week_income': week_income,
        'month_income': month_income,
        'today_services': today_services,
        'staff_count': staff_count,
        'low_inventory': low_inventory,
        'chart_labels': labels,
        'chart_income': income_data,
        'chart_expense': expense_data,
    }
    return render(request, 'core/dashboard.html', context)

# --- Add this below your dashboard view ---

class ServiceRecordForm(forms.ModelForm):
    class Meta:
        model = ServiceRecord
        fields = [
            'customer_name', 'customer_phone', 'service_name', 'cost', 'staff',
            'products_purchased', 'salon_rating', 'staff_rating',
            'phonepe_amount', 'cash_amount'
        ]
        widgets = {
            # ...existing widgets...
            'phonepe_amount': forms.NumberInput(attrs={'placeholder': 'PhonePe Amount', 'class': 'form-control'}),
            'cash_amount': forms.NumberInput(attrs={'placeholder': 'Cash Amount', 'class': 'form-control'}),
        }
def customer_entry(request):
    if request.method == 'POST':
        form = ServiceRecordForm(request.POST)
        if form.is_valid():
            service = form.save()
            # Create a FinancialRecord for the service income
            FinancialRecord.objects.create(
                record_type='income',
                amount=service.cost,
                description=f"Service: {service.service_name} for {service.customer_name}",
                date=service.date.date() if hasattr(service, 'date') else date.today()
            )
            # If products were purchased, add as income (customize as needed)
            if service.products_purchased:
                FinancialRecord.objects.create(
                    record_type='income',
                    amount=0,  # Replace 0 with actual product total if you track it separately
                    description=f"Products sold to {service.customer_name}: {service.products_purchased}",
                    date=service.date.date() if hasattr(service, 'date') else date.today()
                )
            return redirect('dashboard')
    else:
        form = ServiceRecordForm()
    return render(request, 'core/customer_entry.html', {'form': form})
# Staff management
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'phone', 'role', 'is_active']

def staff_list(request):
    staff_members = Staff.objects.all()
    return render(request, 'core/staff_list.html', {'staff_members': staff_members})

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_list')
    else:
        form = StaffForm()
    return render(request, 'core/add_staff.html', {'form': form})

# Inventory management
class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'threshold']

def inventory_list(request):
    inventory_items = InventoryItem.objects.all()
    return render(request, 'core/inventory_list.html', {'inventory_items': inventory_items})

def add_inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'core/add_inventory.html', {'form': form})
def income_detail(request):
    today = date.today()
    incomes = FinancialRecord.objects.filter(record_type='income', date=today)
    services = ServiceRecord.objects.filter(date__date=today)
    return render(request, 'core/income_detail.html', {
        'incomes': incomes,
        'services': services,
        'today': today,
    })
def monthly_income_detail(request):
    today = date.today()
    month_start = today.replace(day=1)
    # Group by day and sum income
    daily_incomes = (
        FinancialRecord.objects
        .filter(record_type='income', date__gte=month_start, date__lte=today)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )
    total_income = sum(item['total'] for item in daily_incomes)
    avg_income = total_income / today.day if today.day else 0
    projected_income = avg_income * 30  # Simple projection for 30-day month

    return render(request, 'core/monthly_income_detail.html', {
        'daily_incomes': daily_incomes,
        'total_income': total_income,
        'avg_income': avg_income,
        'projected_income': projected_income,
        'month': today.strftime('%B %Y'),
    })
def clean(self):
    cleaned_data = super().clean()
    total = (cleaned_data.get('phonepe_amount') or 0) + (cleaned_data.get('cash_amount') or 0)
    cost = cleaned_data.get('cost') or 0
    if total != cost:
        raise forms.ValidationError("Sum of PhonePe and Cash amounts must equal the total cost.")
    return cleaned_data