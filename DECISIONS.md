# Architectural Decisions

## 1. SAP Data (Fuel/Procurement)
- **Format**: Decided to handle **SAP CSV exports** with standard BUKRS/MATNR columns.
- **Complexity**: Handled German column headers (e.g., MATNR for Material) and inconsistent date formats (DD.MM.YYYY).
- **Validation**: Auto-flags records with negative quantities or unrecognized units.

## 2. Utility Data (Electricity)
- **Format**: Handled **Portal CSV exports**.
- **Logic**: Normalizes kWh into kg CO2 using regional grid factors (e.g., 0.85 kg/kWh for India).
- **Ambiguity**: Billing periods spanning multiple months are handled by attributing the entire consumption to the end-date month for simplicity.

## 3. Corporate Travel (Flights)
- **Format**: Handled **Concur-style CSV exports**.
- **Normalization**: Distances are converted from Miles to KM where necessary.
- **Categories**: Differentiates between Short-haul and Long-haul flights for accuracy.

## Resolved Ambiguities
- **Multi-tenancy**: Solved via a `Client` foreign key on all batches.
- **Units**: Implemented a normalization layer in the Python parsers to convert diverse units (L, Gallons, KG, M3) to a standard metric.
- **Review Flow**: Analysts see "Flagged" rows (high CO2 or data anomalies) first to prioritize high-risk data.
