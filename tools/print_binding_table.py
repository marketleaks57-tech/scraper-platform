"""
Print a simple view of account->proxy bindings (based on cookie filenames).
"""

from pathlib import Path

from src.common.paths import COOKIES_DIR


def main():
    """Print account-to-proxy bindings inferred from cookie filenames."""
    print("Account ↔ Proxy bindings (inferred from cookie files):")
    if not COOKIES_DIR.exists():
        print("No cookies directory found:", COOKIES_DIR)
        return

    found = False
    for path in COOKIES_DIR.glob("*.json"):
        found = True
        # filename pattern: source__accId__proxyId.json (proxyId can be empty)
        name = path.name.rsplit(".", 1)[0]
        parts = name.split("__")
        if len(parts) < 2:
            continue
        source = parts[0]
        account_id = parts[1] if len(parts) > 1 else ""
        proxy_id = parts[2] if len(parts) > 2 else "(direct)"
        print(f"- source={source:10s}  account={account_id:10s}  proxy={proxy_id}")
    
    if not found:
        print("No cookie files found.")

if __name__ == "__main__":
    main()
