# Data Model Design

The system implements a multi-tenant, audit-ready data model specifically designed for emissions data ingestion and normalization.

## Core Entities

### 1. Client (Tenant)
- **Purpose**: Implements multi-tenancy.
- **Fields**: Name, slug (for URL routing), and organization metadata.
- **Decision**: Uses slugs to isolate data at the query level.

### 2. IngestionBatch
- **Purpose**: Tracks every upload session.
- **Source-of-truth**: Stores `source_type` (SAP, Utility, Travel), `uploaded_at`, and status.
- **Audit**: Links to the user who performed the ingestion.

### 3. EmissionRecord
- **Purpose**: Normalized data representing a single emission activity.
- **Categorization**: Fields for **Scope 1/2/3**.
- **Normalization**: Stores both `raw_quantity`/`raw_unit` and `normalized_quantity`/`normalized_unit` (kg CO2e).
- **Status**: `pending`, `flagged`, `approved`, `rejected`, `locked`.
- **Logic**: Once `approved`, records are `locked` to prevent audit tampering.

### 4. AuditLog
- **Purpose**: Full traceability.
- **Tracking**: Logs every change, including old/new values, performer, and timestamp.

## Rationale
- **SQLite for Prototype**: Chosen for zero-config deployment on Render.
- **Normalization**: Factors (e.g., 2.68 for Diesel) are stored as constants in parsers but could move to a `Factor` model in production.
