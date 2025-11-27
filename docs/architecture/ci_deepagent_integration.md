# CI DeepAgent Integration

Guidance for integrating DeepAgent workflows into CI.

## Notes
- Ensure CI runners install optional dependencies needed by the test matrix.
- Airflow DAG parsing can be validated by importing `dags/` modules.
- Record any CI-only configuration in this document as the pipeline evolves.
