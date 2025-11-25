
# src/main.py
# Run the CLI from src/cli.py instead of directly starting the server
# This makes 'python -m src.main' the official CLI entry point
import src.cli

if __name__ == "__main__":
    src.cli.app()