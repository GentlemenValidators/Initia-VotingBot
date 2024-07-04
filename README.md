# Telegram Governance Bot

This Telegram bot monitors governance proposals for various blockchain networks based on the Cosmos SDK and notifies users of new proposals.

## Features

- Monitors multiple blockchain networks for new governance proposals.
- Sends notifications to a Telegram chat when new proposals are detected.

## Prerequisites

- Docker
- Docker Compose
- A Telegram bot token

## Getting Started

### Clone the repository

```bash
git clone https://github.com/yourusername/telegram-governance-bot.git
cd telegram-governance-bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
docker-compose up --build
```
Files

    bot.py: The main script for the bot.
    chains.json: Configuration file containing the endpoints for the blockchain networks to monitor.
    Dockerfile: Docker configuration for building the bot's container.
    docker-compose.yml: Docker Compose configuration for setting up the bot's environment.
    requirements.txt: Python dependencies for the bot.
    README.md: Documentation for the project.

Usage

Start the bot by sending the /start command in the Telegram chat. The bot will then send you updates on new governance proposals as they are detected.
