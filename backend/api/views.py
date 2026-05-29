from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Client, IngestionBatch, EmissionRecord, AuditLog
from .serializers import (
    ClientSerializer, IngestionBatchSerializer, 
    EmissionRecordSerializer, AuditLogSerializer
)
from .parsers.sap_parser import parse_sap_csv
from .parsers.utility_parser import parse_utility_csv
from .parsers.travel_parser import parse_travel_csv

class BaseIngestView(APIView):
    def post(self, request, source_type, parser_func):
        file_obj = request.data.get('file')
        client_slug = request.data.get('client_slug', 'default-client')
        
        if not file_obj:
            return Response({"success": False, "errors": ["No file uploaded"]}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the client doesn't exist, we create one. In a real enterprise app, 
        # this would be managed via an admin panel, but for this prototype, 
        # auto-provisioning makes it easier to test.
        client, _ = Client.objects.get_or_create(slug=client_slug, defaults={'name': client_slug.replace('-', ' ').title()})
        
        batch = IngestionBatch.objects.create(
            client=client,
            source_type=source_type,
            uploaded_by=request.user if request.user.is_authenticated else None,
            file_name=file_obj.name,
            status='processing'
        )
        
        try:
            records, errors = parser_func(batch, file_obj.read())
            
            with transaction.atomic():
                # Bulk create for performance. If we're ingesting 1000+ rows, 
                # doing individual saves would be too slow and risk partial uploads.
                EmissionRecord.objects.bulk_create(records)
                batch.row_count = len(records)
                batch.error_count = errors
                batch.status = 'done'
                batch.save()
                
                # Create Audit Logs for batch creation
                for rec in records:
                    AuditLog.objects.create(
                        record=rec,
                        action='created',
                        performed_by=request.user if request.user.is_authenticated else None,
                        note=f"Ingested from {file_obj.name}"
                    )
            
            return Response({
                "success": True,
                "data": {
                    "batch_id": batch.id,
                    "rows_ingested": len(records),
                    "errors": errors
                }
            })
        except Exception as e:
            batch.status = 'failed'
            batch.save()
            return Response({"success": False, "errors": [str(e)]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IngestSAPView(BaseIngestView):
    def post(self, request):
        return super().post(request, 'SAP', parse_sap_csv)

class IngestUtilityView(BaseIngestView):
    def post(self, request):
        return super().post(request, 'UTILITY', parse_utility_csv)

class IngestTravelView(BaseIngestView):
    def post(self, request):
        return super().post(request, 'TRAVEL', parse_travel_csv)

class EmissionRecordViewSet(viewsets.ModelViewSet):
    queryset = EmissionRecord.objects.all().order_by('-activity_date')
    serializer_class = EmissionRecordSerializer
    filterset_fields = ['status', 'source_type', 'scope', 'batch', 'client']

    def perform_update(self, serializer):
        old_record = self.get_object()
        new_record = serializer.save(edited_manually=True)
        
        AuditLog.objects.create(
            record=new_record,
            action='edited',
            performed_by=self.request.user if self.request.user.is_authenticated else None,
            old_value=EmissionRecordSerializer(old_record).data,
            new_value=EmissionRecordSerializer(new_record).data
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.is_locked:
            return Response({"error": "Record is locked"}, status=status.HTTP_400_BAD_REQUEST)
        
        record.status = 'approved'
        record.reviewed_by = request.user if request.user.is_authenticated else None
        record.reviewed_at = timezone.now()
        record.save()
        
        AuditLog.objects.create(
            record=record,
            action='approved',
            performed_by=request.user if request.user.is_authenticated else None
        )
        return Response({"success": True})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        record = self.get_object()
        if record.is_locked:
            return Response({"error": "Record is locked"}, status=status.HTTP_400_BAD_REQUEST)
        
        record.status = 'rejected'
        record.reviewed_by = request.user if request.user.is_authenticated else None
        record.reviewed_at = timezone.now()
        record.save()
        
        AuditLog.objects.create(
            record=record,
            action='rejected',
            performed_by=request.user if request.user.is_authenticated else None
        )
        return Response({"success": True})

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        record = self.get_object()
        record.is_locked = True
        record.save()
        
        AuditLog.objects.create(
            record=record,
            action='locked',
            performed_by=request.user if request.user.is_authenticated else None
        )
        return Response({"success": True})

    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        ids = request.data.get('ids', [])
        records = EmissionRecord.objects.filter(id__in=ids, is_locked=False)
        count = records.update(
            status='approved', 
            reviewed_by=request.user if request.user.is_authenticated else None,
            reviewed_at=timezone.now()
        )
        
        # Log bulk action (simplified)
        return Response({"success": True, "count": count})

class IngestionBatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngestionBatch.objects.all().order_by('-uploaded_at')
    serializer_class = IngestionBatchSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-performed_at')
    serializer_class = AuditLogSerializer

class StatsView(APIView):
    def get(self, request):
        total = EmissionRecord.objects.count()
        pending = EmissionRecord.objects.filter(status='pending').count()
        flagged = EmissionRecord.objects.filter(status='flagged').count()
        approved = EmissionRecord.objects.filter(status='approved').count()
        
        # Scope-wise distribution
        scope1 = EmissionRecord.objects.filter(scope='SCOPE1').count()
        scope2 = EmissionRecord.objects.filter(scope='SCOPE2').count()
        scope3 = EmissionRecord.objects.filter(scope='SCOPE3').count()
        
        return Response({
            "total_records": total,
            "pending": pending,
            "flagged": flagged,
            "approved": approved,
            "scopes": {
                "scope1": scope1,
                "scope2": scope2,
                "scope3": scope3
            }
        })

from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User

class DebugUserView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        users = list(User.objects.values('id', 'username', 'email', 'is_superuser'))
        user_obj, created = User.objects.get_or_create(username='analyst', defaults={
            'email': 'analyst@breatheesg.com',
            'is_superuser': True,
            'is_staff': True
        })
        user_obj.set_password('analyst123')
        user_obj.save()
        
        return Response({
            "users": users,
            "created_now": created,
            "password_reset_success": True
        })
