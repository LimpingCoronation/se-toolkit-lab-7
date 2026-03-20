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
from services.llm_client import LLMClient


def _get_api_client() -> LMSAPIClient:
    """Create API client from config."""
    config = load_config()
    return LMSAPIClient(config["LMS_API_URL"], config["LMS_API_KEY"])


def _get_llm_client() -> LLMClient:
    """Create LLM client from config."""
    config = load_config()
    return LLMClient(
        config["LLM_API_KEY"],
        config["LLM_API_BASE_URL"],
        config["LLM_API_MODEL"],
    )


SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. Use the available tools to gather relevant data
2. Analyze the data and provide a helpful answer
3. If the data shows trends or comparisons, highlight them
4. If you can't answer with the available tools, say so honestly

Capabilities you can help with:
- List available labs and tasks
- Show pass rates and scores for specific labs
- Compare group performance
- Find top students
- Show submission timelines
- Check completion rates

Always be specific with numbers when available. If a user asks about "lab 4" or "lab-04", 
treat them as the same lab (use format "lab-04" for API calls).
"""


def handle_start(user_input: str = "") -> str:
    """Handle /start command - returns welcome message."""
    return """Welcome! I'm your LMS assistant bot.

I can help you with:
• Check system health (/health)
• Browse available labs (/labs)
• View pass rates for any lab (/scores lab-04)
• Answer questions in plain language!

Try asking me things like:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top 5 students in lab 3?"

Use /help to see all commands."""


def handle_help(user_input: str = "") -> str:
    """Handle /help command - lists available commands."""
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab> - Show per-task pass rates for a lab

Or just ask me questions in plain language:
• "What labs are available?"
• "Show scores for lab 4"
• "Which group is best in lab 3?"
• "Who are the top students?"
"""


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
    if not user_input.strip():
        return "I didn't understand. Try asking me a question like 'What labs are available?' or 'Show scores for lab 4'."

    try:
        llm_client = _get_llm_client()
        tools = llm_client.get_tool_definitions()

        # Build conversation messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        # Call LLM with tool calling loop
        response = llm_client.chat_with_tools(messages, tools)

        return response

    except Exception as e:
        # Fallback for LLM errors
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg:
            return "LLM authentication error. The API token may have expired. Please contact the administrator."
        elif "connection" in error_msg:
            return "Cannot connect to the AI service. Please try again in a moment."
        else:
            return f"I had trouble processing that request. Please try rephrasing or use a command like /help."
