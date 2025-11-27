# Documentation Restructuring Report (Legacy)

This legacy note captures the outcomes from an earlier consolidation pass. For the latest restructuring details, refer to `../docs_restructure_report.md`.

## Historical moves
- `docs/ARCHITECTURE.md` was split into `architecture/system_overview.md` and `architecture/scraper_architecture.md`.
- The former root README became `misc/root_overview.md` with supporting pointers in `misc/documentation_index.md`.
- Browser automation, orchestration integrations, and LLM guidance were consolidated under the architecture and workflows folders.
- Database notes moved into `architecture/database_assets.md` (with a legacy appendix).

## Historical folder snapshot
```
docs/
├── architecture/
│   ├── orchestration_design.md
│   ├── pipeline_flow.md
│   ├── scraper_architecture.md
│   └── system_overview.md
├── changelogs/
│   ├── changelog_v4.md
│   ├── changelog_v5.md
│   └── migration_notes.md
├── misc/
│   ├── faq.md
│   ├── glossary.md
│   ├── restructuring_report.md
│   └── roadmap.md
├── onboarding/
│   ├── coding_guidelines.md
│   ├── config_standards.md
│   └── new_scraper_onboarding.md
├── requirements/
│   ├── business_requirements.md
│   ├── technical_requirements.md
│   ├── v4_8_requirements.md
│   └── v5_0_requirements.md
├── troubleshooting/
│   ├── debugging_guide.md
│   ├── error_codes.md
│   └── known_issues.md
└── workflows/
    ├── db_export_flow.md
    ├── llm_flow.md
    ├── proxy_management_flow.md
    └── scraper_run_flow.md
```

The new restructuring report tracks subsequent updates beyond this snapshot.
