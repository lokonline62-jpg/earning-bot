import os
import json
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

GROUP_1_ID = -1001234567890
GROUP_2_ID = -1009876543210

GROUP_1_LINK = "https://t.me/xxxx"
GROUP_2_LINK = "https://t.me/xxxx"

users = {}

# ---------------- DATABASE ----------------
def load():
    global users
    try:
        with open("db.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

def save():
    with open("db.json", "w") as f:
        json.dump(users, f)

# ---------------- JOIN CHECK ----------------
async def joined(user_id, bot):
    try:
        m1 = await bot.get_chat_member(GROUP_1_ID, user_id)
        m2 = await bot.get_chat_member(GROUP_2_ID, user_id)
        return m1.status in ["member", "administrator", "creator"] and m2.status in ["member", "administrator", "creator"]
    except:
        return False

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    if not await joined(user.id, context.bot):
        btn = [
            [InlineKeyboardButton("Join 1", url=GROUP_1_LINK)],
            [InlineKeyboardButton("Join 2", url=GROUP_2_LINK)],
            [InlineKeyboardButton("CHECK", callback_data="check")]
        ]
        await update.message.reply_text("Join both groups first!", reply_markup=InlineKeyboardMarkup(btn))
        return

    if uid not in users:
        users[uid] = {"bal": 0}
        save()

    menu = ReplyKeyboardMarkup(
        [["💰 Balance", "🎯 Earn"], ["💸 Withdraw"]],
        resize_keyboard=True
    )

    await update.message.reply_text("Welcome!", reply_markup=menu)

# ---------------- CHECK BUTTON ----------------
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if await joined(q.from_user.id, context.bot):
        await q.message.reply_text("Done! Use /start")
    else:
        await q.answer("Join first ❌", show_alert=True)

# ---------------- MESSAGE ----------------
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text

    if uid not in users:
        users[uid] = {"bal": 0}

    if text == "💰 Balance":
        await update.message.reply_text(f"Your balance: {users[uid]['bal']}")

    elif text == "🎯 Earn":
        users[uid]["bal"] += 10
        save()
        await update.message.reply_text("You earned 10 coins!")

    elif text == "💸 Withdraw":
        if users[uid]["bal"] >= 50:
            users[uid]["bal"] = 0
            save()
            await update.message.reply_text("Withdraw successful!")
        else:
            await update.message.reply_text("Minimum 50 needed!")

# ---------------- MAIN ----------------
def main():
    load()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check, pattern="check"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))

    app.run_polling()

if __name__ == "__main__":
    main()
