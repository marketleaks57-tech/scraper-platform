# Browser Automation

This document summarizes browser automation options for the platform.

## Engines
- **HTTP engine**: default, no browser required.
- **Selenium/Playwright (pipeline pack)**: currently skeletal; implement or disable via configuration before use.

## Recommendations
- Use HTTP engine for lightweight scraping.
- Add integration tests when enabling browser engines to catch site-specific issues.
