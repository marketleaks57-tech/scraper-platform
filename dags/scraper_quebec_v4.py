"""
Airflow DAG for Quebec source (v4).
"""
from __future__ import annotations

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="quebec",
    dag_id="scraper_quebec_v4",
    description="Quebec pharma scraper v4",
    schedule="0 1 * * *",
    tags=["scraper", "quebec"],
)

