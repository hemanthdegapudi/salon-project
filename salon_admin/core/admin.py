from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Staff, InventoryItem, ServiceRecord, FinancialRecord

admin.site.register(Staff)
admin.site.register(InventoryItem)
admin.site.register(ServiceRecord)
admin.site.register(FinancialRecord)