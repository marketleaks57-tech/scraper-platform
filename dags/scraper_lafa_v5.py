"""Airflow DAG for LAFA scraper using unified pipeline runner."""

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="lafa",
    dag_id="scraper_lafa_v5",
    description="LAFA pharma scraper (unified pipeline v5.0)",
    schedule="0 7 * * *",  # Daily at 7 AM
    tags=["scraper", "lafa", "v5"],
)
