"""
Airflow DAG for Chile source (v4).
"""
from __future__ import annotations

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="chile",
    dag_id="scraper_chile_v4",
    description="Chile pharma scraper v4",
    schedule="15 3 * * *",
    tags=["scraper", "chile"],
)

