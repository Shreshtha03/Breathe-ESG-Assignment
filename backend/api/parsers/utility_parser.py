import csv
import io
from datetime import datetime
from decimal import Decimal
from api.models import EmissionRecord

def parse_utility_csv(batch, file_content):
    """
    Parses Utility CSV content.
    Columns: meter_id, billing_period_start, billing_period_end, 
             consumption_kwh, demand_kw, tariff_code, amount_inr, site_name
    """
    decoded_file = file_content.decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    records = []
    errors = 0
    
    for row in reader:
        try:
            # 1. Billing Period (Start/End)
            start_str = row.get('billing_period_start', '')
            end_str = row.get('billing_period_end', '')
            
            try:
                # Assuming YYYY-MM-DD or DD/MM/YYYY. Let's try ISO first.
                activity_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    activity_date = datetime.strptime(end_str, '%d/%m/%Y').date()
                except ValueError:
                    activity_date = datetime.now().date()
                    flag_reason = f"Invalid date format: {end_str}"
                else:
                    flag_reason = None
            else:
                flag_reason = None

            # 2. Consumption
            consumption = Decimal(row.get('consumption_kwh', '0'))
            
            # Auto-flagging rules
            if consumption > 50000:
                flag_reason = f"Suspiciously high consumption: {consumption} kWh"
            elif consumption < 0:
                flag_reason = "Negative consumption"
            
            # Create EmissionRecord
            record = EmissionRecord(
                batch=batch,
                client=batch.client,
                source_type='UTILITY',
                scope='SCOPE2',
                activity_date=activity_date,
                description=f"Electricity bill for {row.get('site_name', 'Unknown Site')}",
                raw_quantity=consumption,
                raw_unit='kWh',
                normalized_quantity=consumption,
                normalized_unit='kWh',
                co2_kg=consumption * Decimal('0.82'), # Indian Grid Factor
                amount_inr=Decimal(row.get('amount_inr', '0')),
                vendor=row.get('meter_id'), # Use meter_id as reference
                location=row.get('site_name'),
                raw_row=row,
                status='flagged' if flag_reason else 'pending',
                flag_reason=flag_reason
            )
            
            # Check high CO2 flag
            if record.co2_kg > 10000:
                record.status = 'flagged'
                record.flag_reason = f"High CO2 contribution: {record.co2_kg} kg"

            records.append(record)
        except Exception as e:
            errors += 1
            print(f"Error parsing Utility row: {e}")
            
    return records, errors
