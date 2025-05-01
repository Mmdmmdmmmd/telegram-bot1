from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import uuid
import json

# تنظیمات اصلی
TOKEN = "7868052756:AAFrDwy8lGspRDXUhobjEmblwXEIgqNZVzs"
ADMIN_ID = 7394295267
DATA_FILE = "file_map.json"

try:
    with open(DATA_FILE, "r") as f:
        file_map = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    file_map = {}

def save_db():
    with open(DATA_FILE, "w") as f:
        json.dump(file_map, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        code = args[0]
        info = file_map.get(code)
        if not info:
            await update.message.reply_text("کد نامعتبره یا فایل موجود نیست.")
            return

        path = info["file_path"]
        if not os.path.exists(path):
            await update.message.reply_text("فایل حذف شده.")
            return

        if info["type"] == "photo":
            await update.message.reply_photo(photo=InputFile(path))
        elif info["type"] == "video":
            await update.message.reply_video(video=InputFile(path))
        else:
            await update.message.reply_document(document=InputFile(path))
    else:
        await update.message.reply_text("سلام! لطفاً برای دریافت فایل از لینکی استفاده کن که از بات دریافت کردی.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("شما اجازه‌ی ارسال فایل ندارید.")
        return

    file = update.message.document or update.message.video or (update.message.photo[-1] if update.message.photo else None)

    if not file:
        await update.message.reply_text("فایل نامعتبره.")
        return

    code = str(uuid.uuid4())
    file_path = f"files/{code}"
    os.makedirs("files", exist_ok=True)

    telegram_file = await file.get_file()
    await telegram_file.download_to_drive(file_path)

    file_map[code] = {
        "type": "photo" if update.message.photo else (
            "video" if update.message.video else "document"
        ),
        "file_path": file_path
    }
    save_db()

    link = f"https://t.me/downloaderlink012bot?start={code}"  # ← اسم واقعی باتتو بذار اینجا
    await update.message.reply_text(
        f"فایل ذخیره شد!\nلینک دائمی:\n{link}"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))
app.run_polling()

