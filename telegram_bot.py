import os
import asyncio
import logging
import re
import aiofiles
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
MessageHandler,
CallbackQueryHandler,
filters,
ContextTypes,
)

BOT_TOKEN = os.environ.get(“8649532664:AAF8KiRxfSRZHlj_2hZqm0JhP1K7KH59qFM”, “”)
DOWNLOAD_DIR = “downloads”
MAX_SIZE_MB = 50

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

logging.basicConfig(
format=”%(asctime)s - %(name)s - %(levelname)s - %(message)s”,
level=logging.INFO,
)
logger = logging.getLogger(**name**)

SUPPORTED_SITES = [
“youtube.com”, “youtu.be”,
“instagram.com”,
“tiktok.com”, “vm.tiktok.com”,
“twitter.com”, “x.com”,
“facebook.com”, “fb.watch”,
“dailymotion.com”,
“vimeo.com”,
]

def is_valid_url(text):
return bool(re.compile(r”https?://[^\s]+”).match(text.strip()))

def is_supported_url(url):
return any(site in url.lower() for site in SUPPORTED_SITES)

def get_file_size_mb(filepath):
return os.path.getsize(filepath) / (1024 * 1024)

async def download_media(url, format_type, quality):
output_template = os.path.join(DOWNLOAD_DIR, “%(title).50s.%(ext)s”)

```
if format_type == "audio":
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }
else:
    if quality == "1080":
        fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"
    elif quality == "720":
        fmt = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"
    elif quality == "360":
        fmt = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]"
    else:
        fmt = "best[ext=mp4]/best"

    ydl_opts = {
        "format": fmt,
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "concurrent_fragment_downloads": 4,
    }

loop = asyncio.get_event_loop()

def _download():
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if format_type == "audio":
            filename = os.path.splitext(filename)[0] + ".mp3"
        return {
            "filename": filename,
            "title": info.get("title", "Video"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "Unknown"),
        }

return await loop.run_in_executor(None, _download)
```

def quality_keyboard(url):
keyboard = [
[
InlineKeyboardButton(“1080p HD”, callback_data=f”video|1080|{url}”),
InlineKeyboardButton(“720p”, callback_data=f”video|720|{url}”),
],
[
InlineKeyboardButton(“360p (Fast)”, callback_data=f”video|360|{url}”),
InlineKeyboardButton(“MP3 Audio”, callback_data=f”audio|mp3|{url}”),
],
[
InlineKeyboardButton(“Cancel”, callback_data=“cancel”),
],
]
return InlineKeyboardMarkup(keyboard)

async def start_command(update, context):
await update.message.reply_text(
“Welcome to Video Downloader Bot!\n\n”
“Send me a video link from:\n”
“YouTube, Instagram, TikTok, Twitter, Facebook\n\n”
“I will download it for you!”
)

async def help_command(update, context):
await update.message.reply_text(
“Commands:\n”
“/start - Start\n”
“/help - Help\n\n”
“Just send a video link!”
)

async def handle_url(update, context):
url = update.message.text.strip()

```
if not is_valid_url(url):
    await update.message.reply_text("Please send a valid URL!")
    return

if not is_supported_url(url):
    await update.message.reply_text(
        "This site is not supported!\n"
        "Supported: YouTube, Instagram, TikTok, Twitter, Facebook"
    )
    return

await update.message.reply_text(
    "Select quality:",
    reply_markup=quality_keyboard(url),
)
```

async def handle_quality_selection(update, context):
query = update.callback_query
await query.answer()

```
if query.data == "cancel":
    await query.edit_message_text("Cancelled.")
    return

try:
    parts = query.data.split("|", 2)
    format_type, quality, url = parts[0], parts[1], parts[2]
except (ValueError, IndexError):
    await query.edit_message_text("Unknown error.")
    return

if format_type == "audio":
    await query.edit_message_text("Downloading MP3... Please wait.")
else:
    await query.edit_message_text(f"Downloading {quality}p... Please wait.")

filename = None
try:
    info = await download_media(url, format_type, quality)
    filename = info["filename"]

    file_size = get_file_size_mb(filename)
    if file_size > MAX_SIZE_MB:
        await query.edit_message_text(
            f"File too large ({file_size:.1f}MB). Max: {MAX_SIZE_MB}MB\n"
            "Please try lower quality (360p)"
        )
        return

    await query.edit_message_text(f"Sending... ({file_size:.1f}MB)")

    caption = f"{info['title']}\n{info['uploader']}\n{file_size:.1f}MB"

    async with aiofiles.open(filename, "rb") as f:
        file_bytes = await f.read()

    if format_type == "audio":
        await query.message.reply_audio(
            audio=file_bytes,
            caption=caption,
            title=info["title"],
            performer=info["uploader"],
        )
    else:
        await query.message.reply_video(
            video=file_bytes,
            caption=caption,
            supports_streaming=True,
        )

    await query.edit_message_text("Done!")

except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    await query.edit_message_text(f"Error: {str(e)[:200]}")

finally:
    if filename and os.path.exists(filename):
        os.remove(filename)
```

def main():
if not BOT_TOKEN:
print(“BOT_TOKEN not found!”)
return

```
app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .concurrent_updates(True)
    .build()
)

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
app.add_handler(CallbackQueryHandler(handle_quality_selection))

print("Bot started!")
app.run_polling(
    allowed_updates=Update.ALL_TYPES,
    drop_pending_updates=True,
)
```

if **name** == “**main**”:
main()