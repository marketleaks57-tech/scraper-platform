"""Airflow DAG for AlfaBeta scraper using unified pipeline runner."""

from dags.scraper_base import build_scraper_dag

# Create DAG using standardized factory
dag = build_scraper_dag(
    source="alfabeta",
    dag_id="scraper_alfabeta_v5",
    description="AlfaBeta pharma scraper (unified pipeline v5.0)",
    schedule="0 3 * * *",  # Daily at 3 AM
    tags=["scraper", "alfabeta", "pharma", "v5"],
)
