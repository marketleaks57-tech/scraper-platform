# Debugging Guide

1. Reproduce the failure with verbose logging enabled in the orchestrator.
2. Confirm pipeline configuration keys and agent registrations match the orchestrator in use.
3. Check dependency availability before invoking browser engines or database exporters.
4. Use Airflow task logs and dashboard views to isolate failing steps; rerun with narrower scopes if necessary.
5. For merge conflicts or configuration drift, align with the latest defaults and rerun validation checks.
