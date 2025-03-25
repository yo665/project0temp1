from django.db import models
from django.utils.text import slugify

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
