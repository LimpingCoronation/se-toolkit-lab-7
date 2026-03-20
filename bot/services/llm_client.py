"""LLM client with tool calling support for intent routing."""

import httpx
import json
import sys
from typing import Any


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    def _debug(self, message: str) -> None:
        """Print debug message to stderr."""
        print(f"[LLM] {message}", file=sys.stderr)

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return tool definitions for the LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get all labs and tasks from the LMS. Use this to list available labs or find a specific lab/task.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get all enrolled learners and their group assignments. Use this to find how many students are enrolled or to look up a specific student.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed across students.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            }
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a specific lab. Use this to see which tasks are hardest or to show pass rates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            }
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submissions per day for a specific lab. Use this to see activity over time or when students were most active.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            }
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group average scores and student counts for a specific lab. Use this to compare group performance or find the best performing group.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            }
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a specific lab. Use this to show leaderboard or find best students.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top learners to return, e.g. 5, 10",
                            },
                        },
                        "required": ["lab", "limit"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a specific lab. Use this to see what percentage of students completed the lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            }
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL pipeline to sync data from autochecker. Use this when the user asks to refresh or update the data.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> str:
        """Chat with LLM using tool calling loop.

        Args:
            messages: Conversation history with role/content format
            tools: Tool definitions for the LLM
            max_iterations: Maximum tool calling iterations

        Returns:
            Final response from the LLM
        """
        client = self._get_client()

        for iteration in range(max_iterations):
            response = client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            message = choice["message"]

            # Check if LLM wants to call tools
            if "tool_calls" in message and message["tool_calls"]:
                tool_calls = message["tool_calls"]

                # Add assistant's message with tool calls to conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.get("content"),
                        "tool_calls": tool_calls,
                    }
                )

                # Execute each tool call
                for tool_call in tool_calls:
                    function = tool_call["function"]
                    tool_name = function["name"]
                    tool_args = json.loads(function["arguments"])

                    self._debug(f"Tool called: {tool_name}({tool_args})")

                    # Execute the tool
                    result = self._execute_tool(tool_name, tool_args)

                    self._debug(f"Tool result: {len(str(result))} chars")

                    # Add tool result to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result, default=str),
                        }
                    )

                self._debug(f"Feeding {len(tool_calls)} tool result(s) back to LLM")

                # Continue loop to feed results back to LLM
                continue
            else:
                # LLM returned final response
                content = message.get("content", "I couldn't process that request.")
                self._debug(f"Final response: {len(content)} chars")
                return content

        return "I'm having trouble processing this request. Please try rephrasing."

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the LMS API."""
        # Import here to avoid circular imports
        from .api_client import LMSAPIClient
        from ..config import load_config

        config = load_config()
        api_client = LMSAPIClient(config["LMS_API_URL"], config["LMS_API_KEY"])

        tool_methods = {
            "get_items": lambda: api_client.get_labs(),
            "get_learners": lambda: api_client.get_learners(),
            "get_scores": lambda: api_client.get_scores(arguments.get("lab", "")),
            "get_pass_rates": lambda: api_client.get_pass_rates(arguments.get("lab", "")),
            "get_timeline": lambda: api_client.get_timeline(arguments.get("lab", "")),
            "get_groups": lambda: api_client.get_groups(arguments.get("lab", "")),
            "get_top_learners": lambda: api_client.get_top_learners(
                arguments.get("lab", ""), arguments.get("limit", 5)
            ),
            "get_completion_rate": lambda: api_client.get_completion_rate(
                arguments.get("lab", "")
            ),
            "trigger_sync": lambda: api_client.trigger_sync(),
        }

        method = tool_methods.get(name)
        if method:
            return method()
        return {"error": f"Unknown tool: {name}"}
