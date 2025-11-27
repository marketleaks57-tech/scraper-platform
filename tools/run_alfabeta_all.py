import os

from dotenv import load_dotenv

from src.scrapers.alfabeta.pipeline import run_alfabeta


def main():
    """Run AlfaBeta pipeline with environment variables loaded from .env."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    out = run_alfabeta()
    print(f"AlfaBeta run complete. Output: {out}")

if __name__ == "__main__":
    main()
