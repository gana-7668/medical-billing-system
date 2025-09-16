# billing_app/models.py

from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Bill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_per_tablet = models.DecimalField(max_digits=6, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price_per_tablet
