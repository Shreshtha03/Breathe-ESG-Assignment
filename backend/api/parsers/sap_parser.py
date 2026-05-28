import csv
import io
from datetime import datetime
from decimal import Decimal
from api.models import EmissionRecord

def parse_sap_csv(batch, file_content):
    """
    Parses SAP CSV content.
    Columns: BUKRS, BLDAT, MATNR, MENGE, MEINS, WERKS, SGTXT, WRBTR, WAERS
    """
    decoded_file = file_content.decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    records = []
    errors = 0
    
    for row in reader:
        try:
            # 1. Activity Date (BLDAT: DD.MM.YYYY)
            activity_date_str = row.get('BLDAT', '')
            try:
                activity_date = datetime.strptime(activity_date_str, '%d.%m.%Y').date()
            except ValueError:
                # Flag if date format is wrong
                activity_date = datetime.now().date() # fallback
                flag_reason = f"Invalid date format: {activity_date_str}"
            else:
                flag_reason = None

            # 2. Quantity and Units (MENGE, MEINS)
            raw_quantity = Decimal(row.get('MENGE', '0'))
            raw_unit = row.get('MEINS', '').upper()
            
            # Normalize Units (Litter/KG -> Scope 1)
            # For prototype, we assume L and KG are standard.
            normalized_quantity = raw_quantity
            normalized_unit = raw_unit
            
            scope = 'SCOPE1'
            
            # Auto-flagging rules
            if not raw_unit:
                flag_reason = "Missing unit (MEINS)"
            elif raw_unit not in ['L', 'KG', 'M3']:
                flag_reason = f"Unrecognized unit: {raw_unit}"
            
            if raw_quantity < 0:
                flag_reason = "Negative quantity"
            
            # Create EmissionRecord
            record = EmissionRecord(
                batch=batch,
                client=batch.client,
                source_type='SAP',
                scope=scope,
                activity_date=activity_date,
                description=row.get('SGTXT', 'SAP Fuel/Procurement'),
                raw_quantity=raw_quantity,
                raw_unit=raw_unit,
                normalized_quantity=normalized_quantity,
                normalized_unit=normalized_unit,
                currency=row.get('WAERS'),
                amount_inr=Decimal(row.get('WRBTR', '0')), # Simplified
                vendor=row.get('BUKRS'), # Use BUKRS as vendor for now
                location=row.get('WERKS'), # Use WERKS as plant code
                raw_row=row,
                status='flagged' if flag_reason else 'pending',
                flag_reason=flag_reason
            )
            
            # CO2 Calculation (Simplified factors)
            # Diesel: 2.68 kg CO2 per liter, Lub: 2.5 per kg
            if raw_unit == 'L':
                record.co2_kg = raw_quantity * Decimal('2.68')
            elif raw_unit == 'KG':
                record.co2_kg = raw_quantity * Decimal('2.5')
            elif raw_unit == 'M3':
                record.co2_kg = raw_quantity * Decimal('1.9')
            
            # Check high CO2 flag
            if record.co2_kg and record.co2_kg > 10000:
                record.status = 'flagged'
                record.flag_reason = f"High CO2 contribution: {record.co2_kg} kg"

            records.append(record)
        except Exception as e:
            errors += 1
            print(f"Error parsing SAP row: {e}")
            
    return records, errors
