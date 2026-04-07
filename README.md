# Telegram Bot Starter

Simple Telegram bot in Python using `python-telegram-bot`.

## Features

- `/start` command
- `/help` command
- Reads a Yandex Music track URL
- Responds with track name, artist, and duration

## Setup

1. Create a bot in Telegram using [@BotFather](https://t.me/BotFather).
2. Copy your bot token.
3. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Export your token:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

6. Run the bot:

```bash
python bot.py
```

## Notes

- Keep your token private.
- Stop the bot with `Ctrl + C`.
