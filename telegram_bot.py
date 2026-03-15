“””
🤖 بۆتی داونلۆدەری ڤیدیۆ - تیلیگرام
📦 پێویستیەکان:
pip install yt-dlp python-telegram-bot aiohttp aiofiles

🚀 ئەجراکردن:
python telegram_bot.py
“””

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

# ============================

# ⚙️ ڕێکخستنەکان

# ============================

BOT_TOKEN = “TOKEN_ی_بۆتەکەت_ئێرە”  # لێرە تۆکێنەکەت بنووسە
DOWNLOAD_DIR = “downloads”
MAX_SIZE_MB = 50  # سنووری فایل تیلیگرام (50MB)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ============================

# 📋 لۆگینگ

# ============================

logging.basicConfig(
format=”%(asctime)s - %(name)s - %(levelname)s - %(message)s”,
level=logging.INFO,
handlers=[
logging.FileHandler(“bot.log”),
logging.StreamHandler(),
],
)
logger = logging.getLogger(**name**)

# ============================

# 🌐 پشتگیری لینکەکان

# ============================

SUPPORTED_SITES = [
“youtube.com”, “youtu.be”,
“instagram.com”,
“tiktok.com”, “vm.tiktok.com”,
“twitter.com”, “x.com”,
“facebook.com”, “fb.watch”,
“dailymotion.com”,
“vimeo.com”,
]

def is_valid_url(text: str) -> bool:
“”“چێک دەکات ئایا تێکست لینکێکی درووسته”””
url_pattern = re.compile(
r”https?://[^\s]+”
)
return bool(url_pattern.match(text.strip()))

def is_supported_url(url: str) -> bool:
“”“چێک دەکات ئایا سایتەکە پشتگیری دەکرێت”””
return any(site in url.lower() for site in SUPPORTED_SITES)

def get_file_size_mb(filepath: str) -> float:
“”“قەبارەی فایل دەگەڕێنێتەوە بە MB”””
return os.path.getsize(filepath) / (1024 * 1024)

# ============================

# 📥 فانکشنی داونلۆد

# ============================

async def download_media(url: str, format_type: str, quality: str) -> dict:
“””
داونلۆدی میدیا
format_type: ‘video’ یان ‘audio’
quality: ‘360’, ‘720’, ‘1080’, ‘best’
“””
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
        "no_warnings": True,
    }
else:
    # هەڵبژاردنی کوالیتی ڤیدیۆ
    if quality == "1080":
        fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]"
    elif quality == "720":
        fmt = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]"
    elif quality == "360":
        fmt = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]"
    else:
        fmt = "best[ext=mp4]/best"

    ydl_opts = {
        "format": fmt,
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        # ⚡ خێراتر داونلۆد بکات
        "concurrent_fragment_downloads": 4,
        "buffersize": 1024 * 16,
        "http_chunk_size": 10485760,  # 10MB chunks
    }

loop = asyncio.get_event_loop()

def _download():
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # بۆ MP3 پسوندەکە دەگۆڕێت
        if format_type == "audio":
            filename = os.path.splitext(filename)[0] + ".mp3"
        return {
            "filename": filename,
            "title": info.get("title", "ڤیدیۆ"),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "نەزانراو"),
            "thumbnail": info.get("thumbnail", ""),
        }

return await loop.run_in_executor(None, _download)
```

# ============================

# 🎛️ کیبۆردی هەڵبژاردن

# ============================

def quality_keyboard(url: str) -> InlineKeyboardMarkup:
“”“کیبۆردی هەڵبژاردنی کوالیتی”””
keyboard = [
[
InlineKeyboardButton(“🎥 1080p HD”, callback_data=f”video|1080|{url}”),
InlineKeyboardButton(“📹 720p”, callback_data=f”video|720|{url}”),
],
[
InlineKeyboardButton(“📱 360p (خێرا)”, callback_data=f”video|360|{url}”),
InlineKeyboardButton(“🎧 MP3 دەنگ”, callback_data=f”audio|mp3|{url}”),
],
[
InlineKeyboardButton(“❌ پاشگەزبوونەوە”, callback_data=“cancel”),
],
]
return InlineKeyboardMarkup(keyboard)

# ============================

# 🤖 هەندڵەرەکان

# ============================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“کمانی /start”””
welcome_text = (
“👋 **بەخێربێیت بۆ بۆتی داونلۆدەری ڤیدیۆ!**\n\n”
“🎬 **چۆن بەکاربهێنیت:**\n”
“لینکی ڤیدیۆ بنێرە و کوالیتی هەڵبژێرە!\n\n”
“📱 **سایتە پشتگیریکراوەکان:**\n”
“• YouTube 🎬\n”
“• Instagram 📸\n”
“• TikTok 🎵\n”
“• Twitter/X 🐦\n”
“• Facebook 👍\n”
“• Dailymotion 🎥\n”
“• Vimeo 🎞️\n\n”
“✨ **تایبەتمەندیەکان:**\n”
“🎥 هەڵبژاردنی 360p / 720p / 1080p\n”
“🎧 داونلۆدی MP3\n”
“⚡ خێراتر دەنێرێت\n\n”
“لینک بنێرە دەستپێبکە! 👇”
)
await update.message.reply_text(welcome_text, parse_mode=“Markdown”)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“کمانی /help”””
help_text = (
“❓ **ئارشاوی بۆت**\n\n”
“**کمانەکان:**\n”
“/start - دەستپێکردن\n”
“/help - ئارشاو\n”
“/status - حاڵی بۆت\n\n”
“**کێشەکان:**\n”
“• ئەگەر داونلۆد نەکرا، لینکەکە دووبارە بنێرە\n”
“• ڤیدیۆی زیاتر لە 50MB نادرێت\n”
“• ژمارەی کاری لەسەر یەک کات سنووردارە\n\n”
“📧 کێشەت هەیە؟ @YourUsername پەیوەندیم پێوەبکە”
)
await update.message.reply_text(help_text, parse_mode=“Markdown”)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“کمانی /status”””
status_text = (
“✅ **بۆت چالاکە!**\n\n”
f”🖥️ دیرێکتۆری داونلۆد: `{DOWNLOAD_DIR}/`\n”
f”📦 سنووری فایل: `{MAX_SIZE_MB}MB`\n”
“⚡ حاڵ: ئامادەیە”
)
await update.message.reply_text(status_text, parse_mode=“Markdown”)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“هەندڵی لینکی نێردراو”””
url = update.message.text.strip()

```
if not is_valid_url(url):
    await update.message.reply_text(
        "⚠️ تکایە لینکێکی درووست بنێرە!\n"
        "نموونە: https://youtube.com/watch?v=..."
    )
    return

if not is_supported_url(url):
    await update.message.reply_text(
        "❌ ئەم سایتە پشتگیری نادرێت!\n\n"
        "✅ سایتە پشتگیریکراوەکان:\n"
        "YouTube, Instagram, TikTok, Twitter, Facebook..."
    )
    return

# پیشاندانی کیبۆردی هەڵبژاردن
await update.message.reply_text(
    "🎬 **کوالیتی هەڵبژێرە:**\n\n"
    "• 1080p - کوالیتی زۆر باش\n"
    "• 720p - کوالیتی باش\n"
    "• 360p - خێراتر داونلۆد دەبێت\n"
    "• 🎧 MP3 - تەنها دەنگ",
    reply_markup=quality_keyboard(url),
    parse_mode="Markdown",
)
```

async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“هەندڵی هەڵبژاردنی کوالیتی”””
query = update.callback_query
await query.answer()

```
if query.data == "cancel":
    await query.edit_message_text("❌ پاشگەزبووەوە.")
    return

try:
    parts = query.data.split("|", 2)
    format_type, quality, url = parts[0], parts[1], parts[2]
except (ValueError, IndexError):
    await query.edit_message_text("❌ هەڵەی ناشناسراو.")
    return

# پەیامی داونلۆدکردن
if format_type == "audio":
    status_msg = "🎧 **MP3 داونلۆد دەکرێت...**\n⏳ چاوەڕێ بکە"
else:
    status_msg = f"🎥 **{quality}p داونلۆد دەکرێت...**\n⏳ چاوەڕێ بکە"

await query.edit_message_text(status_msg, parse_mode="Markdown")

filename = None
try:
    # داونلۆدکردن
    info = await download_media(url, format_type, quality)
    filename = info["filename"]

    # چێک کردنی قەبارەی فایل
    file_size = get_file_size_mb(filename)
    if file_size > MAX_SIZE_MB:
        await query.edit_message_text(
            f"❌ فایلەکە زۆر گەورەیە ({file_size:.1f}MB)\n"
            f"سنووری تیلیگرام: {MAX_SIZE_MB}MB\n\n"
            "تکایە کوالیتی کەمتر هەڵبژێرە (360p)"
        )
        return

    # نێردنی فایل ⚡
    await query.edit_message_text(
        f"✅ **داونلۆد تەواو بوو!**\n"
        f"📤 دەینێرێت... ({file_size:.1f}MB)",
        parse_mode="Markdown"
    )

    caption = (
        f"🎬 **{info['title']}**\n"
        f"👤 {info['uploader']}\n"
        f"📦 {file_size:.1f}MB"
    )

    async with aiofiles.open(filename, "rb") as f:
        file_bytes = await f.read()

    if format_type == "audio":
        await query.message.reply_audio(
            audio=file_bytes,
            caption=caption,
            parse_mode="Markdown",
            title=info["title"],
            performer=info["uploader"],
        )
    else:
        await query.message.reply_video(
            video=file_bytes,
            caption=caption,
            parse_mode="Markdown",
            supports_streaming=True,  # ⚡ خێراتر پێشان دەدات
        )

    await query.edit_message_text("✅ **نێردرا!** 🎉", parse_mode="Markdown")

except yt_dlp.utils.DownloadError as e:
    err_msg = str(e)
    if "Private" in err_msg or "private" in err_msg:
        msg = "🔒 ئەم ڤیدیۆیە تایبەتیە، نادرێت داونلۆد بکرێت."
    elif "unavailable" in err_msg.lower():
        msg = "❌ ڤیدیۆیەکە بەردەست نییە."
    elif "age" in err_msg.lower():
        msg = "🔞 ڤیدیۆیەکە سنووری تەمەنی هەیە."
    else:
        msg = f"❌ هەڵەی داونلۆد:\n`{err_msg[:200]}`"
    await query.edit_message_text(msg, parse_mode="Markdown")

except Exception as e:
    logger.error(f"هەڵەی نەزانراو: {e}", exc_info=True)
    await query.edit_message_text(
        f"❌ هەڵەیەک رووی دا:\n`{str(e)[:200]}`",
        parse_mode="Markdown"
    )

finally:
    # سڕینەوەی فایل دوای نێردن
    if filename and os.path.exists(filename):
        os.remove(filename)
        logger.info(f"فایل سڕایەوە: {filename}")
```

# ============================

# 🚀 دەستپێکردنی بۆت

# ============================

def main():
“”“دەستپێکردنی سەرەکی”””
if BOT_TOKEN == “8649532664:AAF8KiRxfSRZHlj_2hZqm0JhP1K7KH59qFM”:
print(“❌ تکایە BOT_TOKEN بگۆڕە بە تۆکێنی ڕاستەقینەی بۆتەکەت!”)
return

```
print("🤖 بۆت دەستپێدەکات...")
print("⚡ بۆ پایاندان CTRL+C داگرە")

app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .concurrent_updates(True)   # ☁️ هاوکاتی بۆ کارکردنی 24/7
    .build()
)

# هەندڵەر زیادکردن
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
app.add_handler(CallbackQueryHandler(handle_quality_selection))

print("✅ بۆت ئامادەیە!")
app.run_polling(
    allowed_updates=Update.ALL_TYPES,
    drop_pending_updates=True,   # نەخشەکانی کۆن نەکات
)
```

if **name** == “**main**”:
main()