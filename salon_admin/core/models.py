from django.db import models

# Create your models here.
from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=50)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    supplier = models.CharField(max_length=100, blank=True)
    threshold = models.PositiveIntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ServiceRecord(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    service_name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    phonepe_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    products_purchased = models.TextField(blank=True)
    salon_rating = models.PositiveSmallIntegerField(default=0)
    staff_rating = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.service_name} ({self.date.date()})"

class FinancialRecord(models.Model):
    RECORD_TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    record_type = models.CharField(max_length=10, choices=RECORD_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.record_type.capitalize()} - {self.amount} on {self.date}"