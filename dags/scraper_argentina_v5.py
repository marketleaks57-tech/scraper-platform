"""Airflow DAG for Argentina scraper using unified pipeline runner."""

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="argentina",
    dag_id="scraper_argentina_v5",
    description="Argentina pharma scraper (unified pipeline v5.0)",
    schedule="0 4 * * *",  # Daily at 4 AM
    tags=["scraper", "argentina", "v5"],
)
