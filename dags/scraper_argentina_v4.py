"""
Airflow DAG for Argentina source (v4).
"""
from __future__ import annotations

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="argentina",
    dag_id="scraper_argentina_v4",
    description="Argentina pharma scraper v4",
    schedule="30 2 * * *",
    tags=["scraper", "argentina", "pharma"],
)

