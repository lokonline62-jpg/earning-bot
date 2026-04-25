import json
from telegram import *
from telegram.ext import *

TOKEN = ""
ADMIN_ID = 8783092908
BOT_USERNAME = "@FREEINCOME009879_BOT"

GROUP_1_ID = -1001234567890
GROUP_2_ID = -1009876543210

GROUP_1_LINK = "https://t.me/+xxxx"
GROUP_2_LINK = "https://t.me/+xxxx"

# ---------------- DATABASE ----------------
users = {}
withdraw_requests = {}

def load():
    global users
    try:
        with open("db.json") as f:
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
        return m1.status in ["member","administrator","creator"] and m2.status in ["member","administrator","creator"]
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
        await update.message.reply_text("Join first!", reply_markup=InlineKeyboardMarkup(btn))
        return

    if uid not in users:
        users[uid] = {"bal":0, "ref":0}

        # Referral
        if context.args:
            ref = context.args[0]
            if ref != uid and ref in users:
                users[ref]["bal"] += 10
                users[ref]["ref"] += 1

    save()

    menu = ReplyKeyboardMarkup([
        ["💰 Earn","👥 Refer"],
        ["💳 Balance","💸 Withdraw"],
        ["📢 Support"]
    ], resize_keyboard=True)

    await update.message.reply_text("Welcome PRO Bot 🚀", reply_markup=menu)

# ---------------- CALLBACK ----------------
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if await joined(q.from_user.id, context.bot):
        await q.message.reply_text("✅ Done! Use bot now")
    else:
        await q.answer("Join first ❌", show_alert=True)

# ---------------- MESSAGE ----------------
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text

    if uid not in users:
        users[uid] = {"bal":0,"ref":0}

    if text == "💰 Earn":
        await update.message.reply_text("Refer = 10 টাকা")

    elif text == "👥 Refer":
        link = f"https://t.me/{BOT_USERNAME}?start={uid}"
        d = users[uid]
        await update.message.reply_text(f"{link}\nRef: {d['ref']}\nBal: {d['bal']}")

    elif text == "💳 Balance":
        await update.message.reply_text(f"{users[uid]['bal']} টাকা")

    elif text == "💸 Withdraw":
        if users[uid]["bal"] < 200:
            await update.message.reply_text("Min 200")
        else:
            withdraw_requests[uid] = True
            await update.message.reply_text("Send number + amount")

    elif uid in withdraw_requests:
        num, amt = text.split()
        withdraw_requests.pop(uid)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"ok_{uid}_{amt}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"no_{uid}")]
        ])

        await context.bot.send_message(
            ADMIN_ID,
            f"Withdraw\nUser:{uid}\n{num}\n{amt}",
            reply_markup=kb
        )

    elif text == "📢 Support":
        await update.message.reply_text("Contact admin")

    save()

# ---------------- ADMIN ACTION ----------------
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data

    if not str(q.from_user.id) == str(ADMIN_ID):
        return

    if data.startswith("ok"):
        _, uid, amt = data.split("_")
        users[uid]["bal"] -= int(amt)

        await context.bot.send_message(uid, "✅ Withdraw approved")
        await q.edit_message_text("Approved")

    elif data.startswith("no"):
        _, uid = data.split("_")
        await context.bot.send_message(uid, "❌ Withdraw rejected")
        await q.edit_message_text("Rejected")

    save()

# ---------------- BROADCAST ----------------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg = " ".join(context.args)

    for u in users:
        try:
            await context.bot.send_message(u, msg)
        except:
            pass

# ---------------- RUN ----------------
load()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(check, pattern="check"))
app.add_handler(CallbackQueryHandler(admin_action))
app.add_handler(MessageHandler(filters.TEXT, msg))

print("🔥 PRO BOT RUNNING")
app.run_polling()
