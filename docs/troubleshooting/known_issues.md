# Known Issues

- Browser engines in `src/pipeline_pack/engines/` are placeholders; invoking them will raise errors until implemented.
- Optional dependencies cause crashes if missing and imported globally; isolate imports or guard execution paths.
- Pipeline-pack compatibility requires agent registrations; missing entries result in registry errors.
- Production readiness depends on database connectivity and monitoring configuration—validate before release.
