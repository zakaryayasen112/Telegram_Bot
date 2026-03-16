import os
import yt_dlp
import asyncio
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder,CommandHandler,MessageHandler,CallbackQueryHandler,filters,ContextTypes

TOKEN=os.environ.get("BOT_TOKEN","")

async def start(update,context):
    await update.message.reply_text("Send me a video link!")

async def url(update,context):
    u=update.message.text
    kb=[[InlineKeyboardButton("720p",callback_data="720|"+u),InlineKeyboardButton("360p",callback_data="360|"+u)],[InlineKeyboardButton("MP3",callback_data="mp3|"+u)]]
    await update.message.reply_text("Select:",reply_markup=InlineKeyboardMarkup(kb))

async def btn(update,context):
    q=update.callback_query
    await q.answer()
    d=q.data.split("|",1)
    t,u=d[0],d[1]
    await q.edit_message_text("Downloading...")
    try:
        if t=="mp3":
            opts={"format":"bestaudio","outtmpl":"dl.%(ext)s","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3"}],"quiet":True}
        else:
            opts={"format":"best","outtmpl":"dl.%(ext)s","quiet":True}
        loop=asyncio.get_event_loop()
        def dl():
            with yt_dlp.YoutubeDL(opts) as y:
                y.download([u])
        await loop.run_in_executor(None,dl)
        import glob
        f=glob.glob("dl.*")[0]
        with open(f,"rb") as x:
            b=x.read()
        if t=="mp3":
            await q.message.reply_audio(b)
        else:
            await q.message.reply_video(b)
        os.remove(f)
        await q.edit_message_text("Done!")
    except Exception as e:
        await q.edit_message_text(f"Error: {e}")

app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,url))
app.add_handler(CallbackQueryHandler(btn))
app.run_polling()
