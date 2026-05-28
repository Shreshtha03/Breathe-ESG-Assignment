import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from api.models import Client, IngestionBatch, EmissionRecord
from api.parsers.sap_parser import parse_sap_csv
from api.parsers.utility_parser import parse_utility_csv
from api.parsers.travel_parser import parse_travel_csv

class Command(BaseCommand):
    help = 'Loads sample CSV data for SAP, Utility, and Travel'

    def handle(self, *args, **options):
        # 1. Create Analyst User
        if not User.objects.filter(username='analyst').exists():
            User.objects.create_superuser('analyst', 'admin@example.com', 'breathe123')
            self.stdout.write(self.style.SUCCESS('Created superuser: analyst'))

        # 2. Create Default Client
        client, created = Client.objects.get_or_create(
            slug='breathe-esg-internal',
            defaults={'name': 'Breathe ESG Internal'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created client: Breathe ESG Internal'))

        # 3. Load Sample Files
        sample_dir = os.path.join(settings.BASE_DIR, '..', 'sample_data')
        
        sources = [
            ('sap_sample.csv', 'SAP', parse_sap_csv),
            ('utility_sample.csv', 'UTILITY', parse_utility_csv),
            ('travel_sample.csv', 'TRAVEL', parse_travel_csv),
        ]

        for filename, source_type, parser in sources:
            filepath = os.path.join(sample_dir, filename)
            if not os.path.exists(filepath):
                self.stdout.write(self.style.WARNING(f'File not found: {filepath}'))
                continue

            self.stdout.write(f'Loading {filename}...')
            
            # Create a batch
            batch = IngestionBatch.objects.create(
                client=client,
                source_type=source_type,
                uploaded_by=User.objects.get(username='analyst'),
                file_name=filename,
                status='processing'
            )

            with open(filepath, 'rb') as f:
                records, errors = parser(batch, f.read())
                
                EmissionRecord.objects.bulk_create(records)
                batch.row_count = len(records)
                batch.error_count = errors
                batch.status = 'done'
                batch.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(records)} rows from {filename} ({errors} errors)'))

        self.stdout.write(self.style.SUCCESS('Sample data loading complete.'))
