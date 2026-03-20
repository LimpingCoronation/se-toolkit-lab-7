"""Command handlers for the LMS Telegram bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram - same function works from --test mode,
unit tests, or the Telegram bot.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from services.api_client import LMSAPIClient


def _get_api_client() -> LMSAPIClient:
    """Create API client from config."""
    config = load_config()
    return LMSAPIClient(config["LMS_API_URL"], config["LMS_API_KEY"])


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
    client = _get_api_client()
    result = client.health_check()
    
    if result["healthy"]:
        return f"Backend is healthy. {result['item_count']} items available."
    else:
        return f"Backend error: {result['error']}"


def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - lists available labs."""
    client = _get_api_client()
    items = client.get_labs()
    
    if not items:
        return "No labs available. The backend may be down or has no data."
    
    # Separate labs and tasks (tasks have parent_id pointing to lab)
    labs = [item for item in items if item.get("type") == "lab"]
    tasks = [item for item in items if item.get("type") == "task"]
    
    # Count tasks per lab
    task_counts = {}
    for task in tasks:
        parent_id = task.get("parent_id")
        if parent_id:
            task_counts[parent_id] = task_counts.get(parent_id, 0) + 1
    
    # Format output
    lines = ["Available labs:"]
    for lab in sorted(labs, key=lambda x: x.get("id", 0)):
        lab_id = lab.get("id")
        lab_num = lab.get("title", f"Lab {lab_id}")
        task_count = task_counts.get(lab_id, 0)
        lines.append(f"- {lab_num} ({task_count} tasks)")
    
    return "\n".join(lines)


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - shows per-task pass rates."""
    if not user_input:
        return "Usage: /scores <lab-name> (e.g., /scores lab-04)"
    
    client = _get_api_client()
    result = client.get_pass_rates(user_input)
    
    if result["error"]:
        return f"Error fetching scores: {result['error']}"
    
    if not result["tasks"]:
        return f"No score data available for {user_input}. The lab may not exist or backend is down."
    
    # Format pass rates (API returns: task, avg_score, attempts)
    lines = [f"Pass rates for {user_input}:"]
    for task_data in result["tasks"]:
        task_name = task_data.get("task", "Unknown")
        avg_score = task_data.get("avg_score", 0)
        attempts = task_data.get("attempts", 0)
        lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
    
    return "\n".join(lines)


def handle_intent(user_input: str = "") -> str:
    """Handle natural language queries using LLM (Task 3)."""
    return f"Natural language query: '{user_input}' (will use LLM routing in Task 3)"
