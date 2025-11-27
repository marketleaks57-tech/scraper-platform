# Scraper Run Flow

This flow captures the end-to-end execution path for a typical scrape.

1. **Schedule**: Airflow triggers a DAG run with source context.
2. **Pipeline selection**: Orchestrator loads pipeline definitions and defaults.
3. **Fetch**: HTTP agent retrieves HTML or JSON payloads.
4. **Parse**: HTML parse agent extracts structured fields.
5. **Normalize & QA**: LLM normalizer and QC agents adjust formats and validate records.
6. **Export**: Database or file exporters persist results and emit run metadata.
7. **Observe**: Dashboard surfaces run status, logs, and export health; operators triage failures using troubleshooting guides.
