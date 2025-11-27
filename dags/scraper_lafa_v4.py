"""
Airflow DAG for LAFA source (v4).
"""
from __future__ import annotations

from dags.scraper_base import build_scraper_dag

dag = build_scraper_dag(
    source="lafa",
    dag_id="scraper_lafa_v4",
    description="LAFA scraper v4",
    schedule="45 2 * * *",
    tags=["scraper", "lafa"],
)

