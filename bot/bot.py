"""Telegram bot entry point with --test mode for offline testing."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import handlers from the handlers module (separation of concerns)
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_intent,
)


def run_test_mode(command: str) -> None:
    """Run a command in test mode and print result to stdout."""
    # Parse the command to extract the handler name
    if command.startswith("/"):
        parts = command[1:].split(maxsplit=1)
        handler_name = parts[0]
        user_input = parts[1] if len(parts) > 1 else ""
    else:
        # For natural language queries (Task 3)
        handler_name = "intent"
        user_input = command

    # Route to appropriate handler
    handlers = {
        "start": handle_start,
        "help": handle_help,
        "health": handle_health,
        "labs": handle_labs,
        "scores": handle_scores,
        "intent": handle_intent,
    }

    handler = handlers.get(handler_name)
    if handler:
        result = handler(user_input)
        print(result)
    else:
        print(f"Unknown command: /{handler_name}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command (e.g., --test '/start')",
    )
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        print("Starting Telegram bot (not implemented yet)")
        # TODO: Initialize Telegram bot and start polling


if __name__ == "__main__":
    main()
