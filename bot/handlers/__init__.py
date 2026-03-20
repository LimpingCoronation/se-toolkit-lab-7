"""Command handlers for the LMS Telegram bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram - same function works from --test mode,
unit tests, or the Telegram bot.
"""


def handle_start(user_input: str = "") -> str:
    """Handle /start command - returns welcome message."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help(user_input: str = "") -> str:
    """Handle /help command - lists available commands."""
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab> - Show per-task pass rates for a lab"""


def handle_health(user_input: str = "") -> str:
    """Handle /health command - checks backend status."""
    return "Backend status: OK (placeholder - will check real backend in Task 2)"


def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - lists available labs."""
    return "Available labs: lab-01, lab-02, lab-03, lab-04, lab-05, lab-06, lab-07 (placeholder - will fetch from backend in Task 2)"


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - shows per-task pass rates."""
    if user_input:
        return f"Scores for {user_input}: Task 1: 80%, Task 2: 75%, Task 3: 90% (placeholder - will fetch from backend in Task 2)"
    return "Usage: /scores <lab-name> (e.g., /scores lab-04)"


def handle_intent(user_input: str = "") -> str:
    """Handle natural language queries using LLM (Task 3)."""
    return f"Natural language query: '{user_input}' (will use LLM routing in Task 3)"
