import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import pdfplumber
import os
import re

import os
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

# clean text
def clean_text(text):
    return re.sub(r'\s+', ' ', text).lower()

# read PDF
def read_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + " "
    except Exception as e:
        print("PDF error:", e)

    return clean_text(text)

# PDF handler
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document

    if not file.file_name.endswith(".pdf"):
        await update.message.reply_text("❌ PDF qofa ergi")
        return

    file_path = f"{file.file_id}.pdf"
    new_file = await context.bot.get_file(file.file_id)
    await new_file.download_to_drive(file_path)

    context.user_data["pdf"] = file_path

    await update.message.reply_text("✅ PDF ga'eera\n✏️ Amma maqaa barreessi")

# Name handler
async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "pdf" not in context.user_data:
        await update.message.reply_text("📄 Dura PDF ergaa")
        return

    name = clean_text(update.message.text)
    file_path = context.user_data["pdf"]

    text = read_pdf(file_path)

    print("NAME:", name)
    print("TEXT SAMPLE:", text[:500])

    if not text:
        await update.message.reply_text("❌ PDF hin dubbifamne (scan ta'uu danda'a)")
        return

    # 🔥 STRONG SEARCH (word by word)
    words = name.split()

    found = all(word in text for word in words)

    if found:
        await update.message.reply_text("✅ Passportiin Keessan Baheraa")
    else:
        await update.message.reply_text("❌ Passportiin Keessan Hin Bane")

    os.remove(file_path)
    context.user_data.clear()

# main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()