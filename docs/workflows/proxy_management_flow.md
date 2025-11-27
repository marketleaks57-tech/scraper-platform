# Proxy Management Flow

Browser and HTTP engines should respect proxy policies to avoid blocking and balance traffic.

1. Prefer the HTTP engine for lightweight scrapes; configure proxies at the request layer.
2. If browser automation is required, ensure selenium or playwright dependencies are installed and verified in lower environments before production.
3. Document proxy pools and rotation strategies alongside pipeline definitions so operators can troubleshoot connection issues quickly.
