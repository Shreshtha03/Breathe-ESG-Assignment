from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IngestSAPView, IngestUtilityView, IngestTravelView,
    EmissionRecordViewSet, IngestionBatchViewSet, AuditLogViewSet,
    StatsView
)

router = DefaultRouter()
router.register(r'records', EmissionRecordViewSet)
router.register(r'batches', IngestionBatchViewSet)
router.register(r'audit', AuditLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ingest/sap/', IngestSAPView.as_view(), name='ingest-sap'),
    path('ingest/utility/', IngestUtilityView.as_view(), name='ingest-utility'),
    path('ingest/travel/', IngestTravelView.as_view(), name='ingest-travel'),
    path('stats/', StatsView.as_view(), name='stats'),
]
