# Tradeoffs

Three things deliberately not built:

1. **PDF/OCR Ingestion**: Facilities data often comes as PDFs. While OCR is the "gold standard," it adds significant latency and fragility for a 4-day prototype. We prioritized robust CSV parsing for Portals.
2. **Real-time API Sync**: While Concur/SAP have APIs, they require enterprise OAuth setups. We used file-based ingestion to demonstrate the data model's flexibility without needing sandbox credentials.
3. **Advanced User Permissions**: The prototype uses a simple `analyst/admin` split. Granular RBAC (Role Based Access Control) was traded off for a more detailed Audit Log and Data Model.
