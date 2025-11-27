# New Scraper Onboarding

1. Review the system overview and pipeline flow documents to understand orchestrator expectations.
2. Add source-specific configs to `config/agents/pipelines.yaml`, using `agent` or `name` keys consistently.
3. Keep engines HTTP-only unless browser automation is required and dependencies are installed.
4. Validate end-to-end runs in staging, then update production readiness checklists and changelogs.
