# Bot Development Plan

## Overview

This document outlines the approach for building the LMS Telegram bot across four tasks. The bot allows users to interact with the LMS backend through Telegram, checking system health, browsing labs and scores, and asking questions in plain language.

## Task 1: Plan and Scaffold

The first task establishes the project structure and testable handler architecture. Key decisions:

- **Separation of concerns**: Handlers are pure functions that take input and return text. They don't depend on Telegram, making them testable via `--test` mode, unit tests, or the actual Telegram bot.
- **Entry point**: `bot.py` handles both `--test` mode (for offline testing) and Telegram polling (for production).
- **Configuration**: Environment variables loaded from `.env.bot.secret` using `python-dotenv`.

This scaffold enables rapid iteration — test handlers without deploying to Telegram.

## Task 2: Backend Integration

Replace placeholder handlers with real API calls:

- Create `bot/services/api_client.py` with Bearer token authentication
- Each handler (`/health`, `/labs`, `/scores`) calls the appropriate backend endpoint
- Error handling: backend down produces friendly messages, not crashes
- All URLs and API keys come from environment variables

## Task 3: Intent-Based Natural Language Routing

Add LLM-powered intent routing:

- Create `bot/services/llm_client.py` for LLM API calls
- Define tools for each backend endpoint with clear descriptions
- The LLM decides which tool to call based on user input
- Natural language queries like "what labs are available?" route to `/labs` handler

The key insight: description quality matters more than prompt engineering. Clear tool descriptions help the LLM make correct routing decisions.

## Task 4: Containerize and Deploy

Production deployment:

- Create `bot/Dockerfile` for the bot container
- Add bot as a service in `docker-compose.yml`
- Configure Docker networking (containers use service names, not `localhost`)
- Document deployment process in README
- Deploy to VM and verify end-to-end functionality

## Testing Strategy

- **Test mode**: `uv run bot.py --test "/command"` for quick iteration
- **Telegram testing**: Deploy and test in real Telegram after each task
- **Error scenarios**: Test backend down, invalid commands, missing config

## Git Workflow

For each task:
1. Create issue describing the work
2. Create feature branch (`task-1-scaffold`, etc.)
3. Open PR with `Closes #...` in description
4. Partner review before merge
5. Deploy after merge
