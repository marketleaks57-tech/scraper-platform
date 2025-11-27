"""Airflow DAG for Quebec scraper using unified pipeline runner."""

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="quebec",
    dag_id="scraper_quebec_v5",
    description="Quebec pharma scraper (unified pipeline v5.0)",
    schedule="0 6 * * *",  # Daily at 6 AM
    tags=["scraper", "quebec", "canada", "v5"],
)
