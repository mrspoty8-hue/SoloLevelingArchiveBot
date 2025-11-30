# Overview

This is a Telegram bot for the Solo Leveling anime series that provides episode information and guides. The bot allows users to browse through Season 1 (12 episodes) and Season 2 (13 episodes) via an interactive inline keyboard interface. Users can select seasons and individual episodes to view details and photos related to each episode.

**Key Features:**
- Season selection with inline buttons
- Episode grid navigation (4 columns)
- Auto-forwards episode photos and details from the main channel
- Auto-deletes forwarded messages after 1 hour with user notification
- Back navigation between screens

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Technology**: Python Telegram Bot library (`python-telegram-bot`)
- **Rationale**: Provides a high-level, async-friendly API for building Telegram bots with built-in handlers for commands and callbacks
- **Architecture Pattern**: Event-driven command and callback handling

## Application Structure
- **Main Entry Point**: `main.py` - Contains bot handlers and logic
- **Configuration**: `config.py` - Stores bot settings, messages, and episode metadata
- **Handler Types**:
  - CommandHandler: Processes `/start` command
  - CallbackQueryHandler: Handles inline button interactions (implied by callback_data usage)

## User Interface Flow
- **Navigation Pattern**: Hierarchical menu system
  1. Start → Season selection (Season 1 or 2)
  2. Season → Episode grid (12 episodes per season in 4-column layout)
  3. Episode → Episode details (photo and text information)
  4. Back navigation to return to season selection
- **Interaction Method**: Inline keyboards for all user interactions

## Data Storage Strategy
- **Current Approach**: In-memory dictionaries in `config.py`
- **Episode Metadata Structure**: Nested dictionaries storing:
  - Season name and message_id
  - Episode photo_message_id and details_message_id references
- **Limitation**: Message IDs are initialized as `None`, suggesting they need to be populated (either at runtime or through a setup process)
- **Consideration**: No persistent database; data resets on bot restart

## Message Management
- **Channel Integration**: Bot references a Telegram channel via `CHANNEL_ID`
- **Purpose**: Likely stores episode photos and details as channel messages, with the bot retrieving them via message IDs
- **Approach**: Message forwarding or inline message linking from channel to user conversations

## Episode Coverage
- **Season 1**: 12 episodes
- **Season 2**: 13 episodes
- **Extensibility**: New seasons can be added by creating additional `SEASON_X_INFO` dictionaries

# External Dependencies

## Telegram Bot API
- **Library**: `python-telegram-bot`
- **Usage**: Core bot functionality, message handling, inline keyboards
- **Key Components**: Application, Update, CommandHandler, CallbackQueryHandler

## Logging
- **Standard Library**: Python `logging` module
- **Configuration**: INFO level logging with timestamp, logger name, and message format

## Environment
- **Deployment**: Designed for Replit or similar cloud hosting
- **Bot Token**: Expected to be provided via environment variables (not visible in current code but required for Telegram bot operation)

## Telegram Channel
- **Channel ID**: Configured in `config.py` as `@your_channel_username`
- **Purpose**: Content storage for episode photos and details
- **Requirement**: Channel must be set up and populated with episode content before bot can function fully