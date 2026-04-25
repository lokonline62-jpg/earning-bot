import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

users = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    if uid not in users:
        users[uid] = {"bal": 0}

    menu = ReplyKeyboardMarkup(
        [["💰 Balance", "💸 Withdraw"]],
        resize_keyboard=True
    )

    await update.message.reply_text("Welcome Bot 🚀", reply_markup=menu)

# Message handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text

    if uid not in users:
        users[uid] = {"bal": 0}

    if text == "💰 Balance":
        bal = users[uid]["bal"]
        await update.message.reply_text(f"Your Balance: {bal}")

    elif text == "💸 Withdraw":
        await update.message.reply_text("Minimum withdraw not set yet.")

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot running...")
    app.run_polling()

# Correct entry point
if __name__ == "__main__":
    main()
