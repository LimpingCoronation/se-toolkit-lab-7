"""Inline keyboard definitions for the Telegram bot."""


def get_start_keyboard() -> list[list[dict[str, str]]]:
    """Get inline keyboard for /start command."""
    return [
        [
            {"text": "🏥 Health Check", "callback_data": "cmd_health"},
            {"text": "📚 Labs", "callback_data": "cmd_labs"},
        ],
        [
            {"text": "📊 Scores", "callback_data": "cmd_scores"},
            {"text": "❓ Help", "callback_data": "cmd_help"},
        ],
        [
            {"text": "💬 Ask a question", "callback_data": "cmd_ask"},
        ],
    ]


def get_help_keyboard() -> list[list[dict[str, str]]]:
    """Get inline keyboard for /help command."""
    return [
        [
            {"text": "🏥 Health", "callback_data": "cmd_health"},
            {"text": "📚 Labs", "callback_data": "cmd_labs"},
            {"text": "📊 Scores", "callback_data": "cmd_scores"},
        ],
        [
            {"text": "💬 Ask a question", "callback_data": "cmd_ask"},
        ],
    ]


def get_scores_keyboard() -> list[list[dict[str, str]]]:
    """Get inline keyboard with common labs for scores."""
    return [
        [
            {"text": "Lab 01", "callback_data": "scores_lab-01"},
            {"text": "Lab 02", "callback_data": "scores_lab-02"},
            {"text": "Lab 03", "callback_data": "scores_lab-03"},
        ],
        [
            {"text": "Lab 04", "callback_data": "scores_lab-04"},
            {"text": "Lab 05", "callback_data": "scores_lab-05"},
            {"text": "Lab 06", "callback_data": "scores_lab-06"},
        ],
        [
            {"text": "◀️ Back", "callback_data": "cmd_help"},
        ],
    ]


def get_ask_keyboard() -> list[list[dict[str, str]]]:
    """Get inline keyboard with suggested questions."""
    return [
        [
            {"text": "What labs are available?", "callback_data": "ask_what_labs"},
        ],
        [
            {"text": "Which lab is hardest?", "callback_data": "ask_hardest"},
        ],
        [
            {"text": "Top students?", "callback_data": "ask_top"},
        ],
    ]


KEYBOARD_CALLBACKS = {
    "cmd_health": "/health",
    "cmd_labs": "/labs",
    "cmd_scores": "/scores ",
    "cmd_help": "/help",
    "cmd_ask": "What can you help me with?",
    "ask_what_labs": "what labs are available",
    "ask_hardest": "which lab has the lowest pass rate",
    "ask_top": "who are the top 5 students in lab 04",
}


def get_callback_command(callback_data: str) -> str:
    """Convert callback data to command string."""
    return KEYBOARD_CALLBACKS.get(callback_data, "")
