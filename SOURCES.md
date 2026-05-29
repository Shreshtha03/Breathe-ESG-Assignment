# Sources and Research

## 1. SAP (Fuel & Logistics)
- **Research**: Studied standard SAP table exports (e.g., MSEG for material documents).
- **Implementation**: Used a flat CSV structure reflecting a typical SAP GUI export.
- **Edge Cases**: Handling plant codes (WERKS) as location metadata.

## 2. Utility Portals
- **Research**: Looked at dummy exports from utility providers.
- **Implementation**: Handles meter readings, billing amounts, and net-consumption values.
- **Justification**: facilities teams usually download CSVs from portals when APIs aren't available.

## 3. Corporate Travel
- **Research**: Analyzed Navan/Concur travel report structures.
- **Implementation**: Captures Departure/Arrival, Class (Economy/Business), and Category (Flight/Hotel).
- **Normalization**: Maps diverse categories to standard Scope 3.6 (Business Travel) emission factors.
