from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, IngestionBatch, EmissionRecord, AuditLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class IngestionBatchSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = IngestionBatch
        fields = '__all__'

class EmissionRecordSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    batch_file_name = serializers.CharField(source='batch.file_name', read_only=True)
    
    class Meta:
        model = EmissionRecord
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
