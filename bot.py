import logging
import os
import re
from urllib.parse import urlparse

import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

YANDEX_TRACK_URL_RE = re.compile(
    r"(?:https?://)?music\.yandex\.ru/album/(?P<album_id>\d+)/track/(?P<track_id>\d+)"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name if update.effective_user else "there"
    await update.message.reply_text(
        f"Hi, {user_first_name}! I am your Telegram bot.\n"
        "Send me a Yandex Music track URL and I will return track info.\n"
        "Type /help to see commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "Send link format:\n"
        "https://music.yandex.ru/album/<album_id>/track/<track_id>"
    )


def _format_duration(ms: int | None) -> str:
    if not ms:
        return "unknown"
    total_seconds = ms // 1000
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def _extract_track_url(text: str) -> str | None:
    for part in text.split():
        parsed = urlparse(part)
        if "music.yandex.ru" in parsed.netloc and "/track/" in parsed.path:
            return part
    return None


def _get_track_data(url: str) -> dict | None:
    match = YANDEX_TRACK_URL_RE.search(url)
    if not match:
        return None

    album_id = match.group("album_id")
    track_id = match.group("track_id")
    endpoint = f"https://music.yandex.ru/handlers/track.jsx?track={track_id}:{album_id}"

    response = requests.get(endpoint, timeout=10)
    response.raise_for_status()
    payload = response.json()
    track = payload.get("track")
    if not track:
        return None

    title = track.get("title", "unknown")
    artists = ", ".join(artist.get("name", "") for artist in track.get("artists", [])) or "unknown"
    duration = _format_duration(track.get("durationMs"))
    return {"title": title, "artists": artists, "duration": duration}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    url = _extract_track_url(update.message.text)
    if not url:
        await update.message.reply_text(
            "Please send a Yandex Music track URL.\n"
            "Example: https://music.yandex.ru/album/123/track/456"
        )
        return

    try:
        track_data = _get_track_data(url)
    except Exception:
        logger.exception("Failed to load track data")
        await update.message.reply_text(
            "Could not fetch track data from Yandex Music for this URL."
        )
        return

    if not track_data:
        await update.message.reply_text(
            "Could not parse track URL or track was not found."
        )
        return

    await update.message.reply_text(
        "Track info:\n"
        f"Name: {track_data['title']}\n"
        f"Artist: {track_data['artists']}\n"
        f"Duration: {track_data['duration']}"
    )


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set. Export it before running the bot.")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
