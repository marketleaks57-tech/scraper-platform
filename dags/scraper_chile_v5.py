"""Airflow DAG for Chile scraper using unified pipeline runner."""

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="chile",
    dag_id="scraper_chile_v5",
    description="Chile pharma scraper (unified pipeline v5.0)",
    schedule="0 5 * * *",  # Daily at 5 AM
    tags=["scraper", "chile", "v5"],
)
