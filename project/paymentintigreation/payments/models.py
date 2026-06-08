from django.db import models

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    name = models.CharField(max_length=150)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Store in INR, e.g. 500.00
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.amount} INR ({self.status})"
