import uuid
from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class IngestionBatch(models.Model):
    SOURCE_CHOICES = [
        ('SAP', 'SAP'),
        ('UTILITY', 'Utility Portals'),
        ('TRAVEL', 'Corporate Travel'),
    ]
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='batches')
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.source_type} - {self.uploaded_at}"

class EmissionRecord(models.Model):
    SCOPE_CHOICES = [
        ('SCOPE1', 'Scope 1'),
        ('SCOPE2', 'Scope 2'),
        ('SCOPE3', 'Scope 3'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('flagged', 'Flagged'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    SOURCE_CHOICES = IngestionBatch.SOURCE_CHOICES

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE, related_name='records')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='records')
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    
    activity_date = models.DateField()
    description = models.CharField(max_length=255)
    
    raw_quantity = models.DecimalField(max_digits=20, decimal_places=5)
    raw_unit = models.CharField(max_length=50)
    
    normalized_quantity = models.DecimalField(max_digits=20, decimal_places=5)
    normalized_unit = models.CharField(max_length=50)
    
    co2_kg = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    
    currency = models.CharField(max_length=10, null=True, blank=True)
    amount_inr = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    vendor = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    raw_row = models.JSONField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    flag_reason = models.CharField(max_length=255, null=True, blank=True)
    
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_records')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_manually = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.description} ({self.activity_date})"

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50) # created/edited/approved/rejected/locked
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} on {self.record.id}"
