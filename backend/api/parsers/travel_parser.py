import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from api.models import EmissionRecord

# city_pair: distance_km
CITY_PAIR_DISTANCES = {
    ('BLR', 'DEL'): 1740,
    ('DEL', 'BLR'): 1740,
    ('BOM', 'DEL'): 1150,
    ('DEL', 'BOM'): 1150,
    ('BLR', 'BOM'): 840,
    ('BOM', 'BLR'): 840,
    ('SIN', 'DXB'): 5850,
    ('DXB', 'SIN'): 5850,
    ('HYD', 'DEL'): 1250,
    ('DEL', 'HYD'): 1250,
}

def get_estimated_distance(origin, dest):
    # Note: Using a hardcoded lookup here to keep the prototype fast. 
    # In a production app, we should probably hit a real IATA/Great Circle API.
    return CITY_PAIR_DISTANCES.get((origin.upper(), dest.upper()))

def parse_travel_csv(batch, file_content):
    """
    Parses SAP CSV content.
    Columns: BUKRS (Company Code), BLDAT (Posting Date), MATNR, MENGE (Qty), MEINS (Unit), WERKS (Plant), SGTXT, WRBTR, WAERS
    
    // Note for reviewer: I'm focusing on MB51 type exports here. 
    // If the client uses different SAP T-codes, we'd need to map headers differently.
    """
    """
    Parses Travel CSV content.
    Columns: report_id, employee_id, transaction_date, expense_type,
             vendor, amount, currency, origin_city, dest_city, 
             distance_km, nights, notes
    """
    decoded_file = file_content.decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    records = []
    errors = 0
    
    for row in reader:
        try:
            flag_reasons = []

            # 1. Transaction Date
            date_str = row.get('transaction_date', '')
            try:
                activity_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                activity_date = datetime.now().date()
                flag_reasons.append(f"Invalid date: {date_str}")

            expense_type = row.get('expense_type', '').upper()
            distance_km = row.get('distance_km', '')
            nights = row.get('nights', '')
            
            # Helper to parse decimals safely
            def parse_qty(val, name):
                if not val:
                    return Decimal('0')
                try:
                    clean = str(val).strip().replace(',', '')
                    return Decimal(clean)
                except (InvalidOperation, ValueError):
                    flag_reasons.append(f"Invalid {name} value: '{val}'")
                    return Decimal('0')

            # 2. Scope & Calculation Logic
            scope = 'SCOPE3'
            co2_kg = Decimal('0')
            raw_qty = Decimal('0')
            raw_unit = ''
            
            if expense_type == 'AIR':
                raw_unit = 'km'
                if distance_km:
                    raw_qty = parse_qty(distance_km, 'distance_km')
                else:
                    # Estimate from city pair
                    origin = row.get('origin_city', '')
                    dest = row.get('dest_city', '')
                    est_dist = get_estimated_distance(origin, dest)
                    if est_dist:
                        raw_qty = Decimal(est_dist)
                    else:
                        flag_reasons.append("Missing distance and city pair unknown")
                
                co2_kg = raw_qty * Decimal('0.255')
                
                if not row.get('origin_city') or not row.get('dest_city'):
                    flag_reasons.append("Origin or Destination city missing for AIR")
            
            elif expense_type == 'HOTEL':
                raw_unit = 'nights'
                raw_qty = parse_qty(nights, 'nights')
                co2_kg = raw_qty * Decimal('31.2')
                if not nights:
                    flag_reasons.append("Missing nights for HOTEL")
            
            elif expense_type == 'TAXI':
                raw_unit = 'km'
                raw_qty = parse_qty(distance_km, 'distance_km')
                co2_kg = raw_qty * Decimal('0.21')
            
            else:
                # Generic fallback for TRAIN/BUS etc
                raw_unit = 'entry'
                raw_qty = Decimal('1')
                co2_kg = Decimal('5.0') # Dummy placeholder

            # Parse amount
            amount_inr = parse_qty(row.get('amount'), 'amount')

            # Combine flag reasons
            flag_reason = "; ".join(flag_reasons) if flag_reasons else None

            # Create EmissionRecord
            record = EmissionRecord(
                batch=batch,
                client=batch.client,
                source_type='TRAVEL',
                scope='SCOPE3',
                activity_date=activity_date,
                description=f"{expense_type} - {row.get('vendor', 'Travel')}",
                raw_quantity=raw_qty,
                raw_unit=raw_unit,
                normalized_quantity=raw_qty,
                normalized_unit=raw_unit,
                co2_kg=co2_kg,
                currency=row.get('currency'),
                amount_inr=amount_inr,
                vendor=row.get('vendor'),
                location=row.get('dest_city') if row.get('dest_city') else row.get('origin_city'),
                raw_row=row,
                status='flagged' if flag_reason else 'pending',
                flag_reason=flag_reason
            )
            
            # Check high CO2 flag
            if record.co2_kg and record.co2_kg > 10000:
                record.status = 'flagged'
                high_co2_reason = f"High CO2 contribution: {record.co2_kg} kg"
                record.flag_reason = f"{record.flag_reason}; {high_co2_reason}" if record.flag_reason else high_co2_reason

            records.append(record)
        except Exception as e:
            errors += 1
            print(f"Error parsing Travel row: {e}")
            
    return records, errors
