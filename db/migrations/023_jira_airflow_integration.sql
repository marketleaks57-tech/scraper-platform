-- 023_jira_airflow_integration.sql: Add fields for Jira-Airflow integration

-- Add Jira and Airflow tracking fields to scraper_runs table
ALTER TABLE scraper.scraper_runs
    ADD COLUMN IF NOT EXISTS jira_issue_key TEXT,
    ADD COLUMN IF NOT EXISTS airflow_dag_id TEXT,
    ADD COLUMN IF NOT EXISTS airflow_dag_run_id TEXT,
    ADD COLUMN IF NOT EXISTS run_type TEXT DEFAULT 'FULL_REFRESH';

-- Add indexes for querying by Jira or Airflow IDs
CREATE INDEX IF NOT EXISTS idx_scraper_runs_jira_issue_key
    ON scraper.scraper_runs (jira_issue_key)
    WHERE jira_issue_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_scraper_runs_airflow_dag_run
    ON scraper.scraper_runs (airflow_dag_id, airflow_dag_run_id)
    WHERE airflow_dag_id IS NOT NULL AND airflow_dag_run_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN scraper.scraper_runs.jira_issue_key IS 'Jira issue key (e.g., SCRAPE-123) that triggered this run';
COMMENT ON COLUMN scraper.scraper_runs.airflow_dag_id IS 'Airflow DAG ID (e.g., scraper_alfabeta)';
COMMENT ON COLUMN scraper.scraper_runs.airflow_dag_run_id IS 'Airflow DAG run ID';
COMMENT ON COLUMN scraper.scraper_runs.run_type IS 'Type of run: FULL_REFRESH, DELTA, or SINGLE_PRODUCT';

