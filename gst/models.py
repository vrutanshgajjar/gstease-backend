
from django.db import models
from django.contrib.auth.models import User

class  Gst_User(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    gstin = models.CharField(max_length=15, unique=True)
    pan = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=255,null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"(({self.id})"
class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=100)
    date = models.DateField()
    gstin = models.CharField(max_length=15, blank=True, null=True)
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField(blank=True, null=True)
    cgst = models.FloatField(default=0.0)
    sgst = models.FloatField(default=0.0)
    igst = models.FloatField(default=0.0)
    total_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    ITC_STATUS_CHOICES = [
        ('claimed', 'Claimed'),
        ('pending', 'Pending'),
        ('reversed', 'Reversed'),
    ]
    itc_status = models.CharField(
    max_length=10,
    choices=ITC_STATUS_CHOICES,
    default='pending'
    )

    def __str__(self):
        return f"Invoice #{self.invoice_no} - {self.customer_name}"
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.FloatField()
    amount = models.FloatField()

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.rate})"
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase_no = models.CharField(max_length=100)
    date = models.DateField()
    supplier_name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    supplier_address = models.TextField(blank=True, null=True)
    cgst = models.FloatField(default=0.0)
    sgst = models.FloatField(default=0.0)
    igst = models.FloatField(default=0.0)
    total_amount = models.FloatField()
    ITC_STATUS_CHOICES = [
        ('claimed', 'Claimed'),
        ('pending', 'Pending'),
        ('reversed', 'Reversed'),
    ]
    itc_status = models.CharField(
    max_length=10,
    choices=ITC_STATUS_CHOICES,
    default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase #{self.purchase_no} - {self.supplier_name}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.FloatField()
    amount = models.FloatField()

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.rate})"
class RecentActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    action = models.CharField(max_length=10, choices=[('claim', 'Claim'), ('reverse', 'Reverse')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.action} {self.invoice_number} at {self.timestamp}"