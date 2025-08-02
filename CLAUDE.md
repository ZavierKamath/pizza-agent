# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a voice-enabled pizza ordering assistant for Zavier's Pizza that integrates Deepgram's conversational AI with Twilio for telephony. The system handles real-time audio streaming and provides function calling capabilities for pizza ordering operations.

## Architecture

The application consists of three main components:

1. **WebSocket Server** (`main.py`): Handles Twilio telephony connections and manages bidirectional audio streaming
2. **Function Registry** (`pizza_functions.py`): Contains business logic for pizza ordering operations (menu, orders, lookups)
3. **Agent Configuration** (`config.json`): Defines the conversational AI agent's behavior, prompts, and available functions

### Key Data Flow
- Twilio receives phone calls and streams audio via WebSocket to the server
- Server forwards audio to Deepgram's agent API for speech-to-text and AI processing
- Agent can call functions from the registry when appropriate
- Deepgram returns synthesized speech that flows back through Twilio to the caller

## Environment Setup

```bash
# Install dependencies
uv sync

# Environment variables are already set up in .env

# Run the server
uv run main.py
```

## Development Commands

- **Start server**: `uv run main.py` (runs on localhost:5000)
- **Install dependencies**: `uv sync`
- **Add dependencies**: `uv add package_name`

## Function System

Functions are registered in `pizza_functions.py` via the `FUNCTION_MAP` dictionary. Current functions:

- **get_menu()**: Returns the complete Zavier's Pizza menu with specialty pizzas, sizes, toppings, sides, and drinks
- **place_pizza_order()**: Handles complete orders with customer info, order type (pickup/delivery), and multiple items with customizations
- **lookup_order()**: Retrieves existing order details by order ID

Each function must:
- Accept keyword arguments matching the schema in `config.json`
- Return a JSON-serializable result
- Handle errors gracefully with error objects

When adding new functions:
1. Implement the function in `pizza_functions.py`
2. Add it to `FUNCTION_MAP`
3. Define the schema in `config.json` under `agent.think.functions`

## Important Notes

- The server expects Twilio WebSocket connections with specific media format (mulaw, 8kHz)
- Audio buffering uses 20x160 byte chunks for optimal streaming
- Function call responses must include the original function ID for proper correlation
- Pizza menu includes specialty pizzas, build-your-own options, multiple sizes, and comprehensive toppings
- The agent prompt in `config.json` should be updated when changing available functions
- Pizza orders require customer name, phone, order type, and address (for delivery)
- Items array supports pizzas with sizes/toppings, sides, and drinks with proper validation