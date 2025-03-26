from django.db import models
from django.utils.text import slugify
from django.utils import timezone

# Generic Models
class Service(models.Model):
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    heading = models.CharField(max_length=255)
    form_name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.heading)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.heading

class Field(models.Model):
    value = models.CharField(max_length=255)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='fields')

class SubContent(models.Model):
    subcontent_number = models.IntegerField()
    heading = models.CharField(max_length=255)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subcontents')

    def __str__(self):
        return f"{self.subcontent_number} - {self.heading}"

class SubContentField(models.Model):
    value = models.CharField(max_length=255)
    subcontent = models.ForeignKey(SubContent, on_delete=models.CASCADE, related_name='subcontent_fields')

class GenericForm(models.Model):    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    city_pincode = models.CharField(max_length=20, null=True, blank=True)
    updates_on_whatsapp = models.BooleanField(default=False)
    status = models.CharField(max_length=255, null=True, blank=True)
    service = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Forms"

# Real Models
class QueryForm(models.Model):    
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    query = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class ConsultationForm(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    date = models.DateField()
    email = models.EmailField()
    query = models.TextField(null=True, blank=True)
    service = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductField(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='fields')
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.name} - {self.value}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Product/Service information
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    
    # Guest user information
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Order details
    order_number = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    user_status = models.CharField(max_length=150, null=True, blank=True)  # Note: lowercase 'u' for consistency

    def __str__(self):
        return f"Order #{self.order_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number if not provided
            self.order_number = f"ORD-{self.created_at.strftime('%Y%m%d%H%M%S')}" if self.created_at else f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        if not self.final_price:
            self.final_price = self.base_price
        super().save(*args, **kwargs)