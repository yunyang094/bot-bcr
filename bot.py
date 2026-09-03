import os, json, random, asyncio
from flask import Flask, request
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from zoneinfo import ZoneInfo
from datetime import time

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/+xxxx")
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")
ADMIN_LINK = os.getenv("ADMIN_LINK", f"tg://user?id={ADMIN_ID}")
FILE_ICON = "premium_icons.json"

# Icon
try:
    icons = json.load(open(FILE_ICON, "r", encoding="utf-8")) if os.path.exists(FILE_ICON) else {}
except:
    icons = {}
reverse_icons = {str(v): k for k, v in icons.items()}
def save_icons():
    try:
        json.dump(icons, open(FILE_ICON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except: pass

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Nhóm Kín", url=GROUP_LINK),
         InlineKeyboardButton("👤 Admin", url=ADMIN_LINK)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="quay_thuong"),
         InlineKeyboardButton("📊 Thống Kê", callback_data="thong_ke")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context):
    await update.message.reply_text(f"✅ Bot chạy OK! {len(icons)} icon", reply_markup=main_keyboard())
async def lich(update: Update, context):
    await update.message.reply_text("Lịch 20:00 sẽ tự đăng!", reply_markup=main_keyboard())
async def xemicon(update: Update, context):
    if not icons:
        await update.message.reply_text("Chưa có icon!"); return
    list_ids = list(icons.values())[:5]
    text = "  " * len(list_ids)
    entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
    await update.message.reply_text(f"Test {len(icons)} icon:\n{text}", entities=entities, reply_markup=main_keyboard())
async def welcome_new_member(update: Update, context):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(f"Chào mừng {member.first_name}!", reply_markup=main_keyboard())
async def button_callback(update: Update, context):
    q = update.callback_query
    await q.answer()
    if q.data == "quay_thuong":
        thuong = random.choice(["🎉 Trúng 10K!", "🎁 Vé miễn phí!", "💎 VIP 1 ngày!", "🔥 Trúng 50K!"])
        await q.message.reply_text(f"🎰 {thuong}", reply_markup=main_keyboard())
    else:
        await q.message.reply_text(f"📊 Icon: {len(icons)}", reply_markup=main_keyboard())
async def save_icon(update: Update, context):
    if not update.message or not update.message.entities: return
    new = 0
    for e in update.message.entities:
        if e.type == MessageEntity.CUSTOM_EMOJI:
            cid = str(e.custom_emoji_id)
            if cid not in reverse_icons:
                icons[f"icon_{len(icons)+1}"] = cid
                reverse_icons[cid] = f"icon_{len(icons)+1}"
                new += 1
    if new: save_icons()

# Tao App Telegram
telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("lich", lich))
telegram_app.add_handler(CommandHandler("xemicon", xemicon))
telegram_app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
telegram_app.add_handler(CallbackQueryHandler(button_callback))
telegram_app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), save_icon))

# Flask Webhook - BAO CHAY 100% TREN PYTHON 3.14
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Bot BCR dang chay!"

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        # Chay async trong sync
        asyncio.run(telegram_app.process_update(update))
    except Exception as e:
        print(f"Loi webhook: {e}")
    return "OK", 200

@flask_app.route("/setwebhook")
def setwebhook():
    url = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or request.host_url
    full = f"{url.rstrip('/')}/webhook"
    try:
        asyncio.run(telegram_app.bot.set_webhook(full, drop_pending_updates=True))
        return f"Da set webhook: {full}"
    except Exception as e:
        return f"Loi: {e}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    # Tu dong set webhook khi khoi dong
    url = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if url:
        try:
            async def _set():
                await telegram_app.bot.set_webhook(f"{url.rstrip('/')}/webhook", drop_pending_updates=True)
                print(f"Set webhook: {url}/webhook")
            asyncio.run(_set())
        except Exception as e:
            print(f"Chua set duoc webhook: {e}")
    flask_app.run(host="0.0.0.0", port=port)
