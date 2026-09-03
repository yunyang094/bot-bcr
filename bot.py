import os, json, random, asyncio
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# FIX cho Python 3.14
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/+xxxx")
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")
ADMIN_LINK = os.getenv("ADMIN_LINK", f"tg://user?id={ADMIN_ID}")
FILE_ICON = "premium_icons.json"

try:
    icons = json.load(open(FILE_ICON, "r", encoding="utf-8")) if os.path.exists(FILE_ICON) else {}
except:
    icons = {}

reverse_icons = {str(v): k for k, v in icons.items()}

def save_icons():
    try:
        json.dump(icons, open(FILE_ICON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except:
        pass

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Nhóm Kín", url=GROUP_LINK),
         InlineKeyboardButton("👤 Admin", url=ADMIN_LINK)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="quay_thuong"),
         InlineKeyboardButton("📊 Thống Kê", callback_data="thong_ke")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Bot BCR chạy OK! {len(icons)} icon", reply_markup=main_keyboard())

async def xemicon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not icons:
        await update.message.reply_text("Chưa có icon nào!")
        return
    list_ids = list(icons.values())[:5]
    text = "  " * len(list_ids)
    entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
    await update.message.reply_text(f"Test {len(icons)} icon:\n{text}", entities=entities, reply_markup=main_keyboard())

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(f"Chào mừng {member.first_name} vào nhóm!", reply_markup=main_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "quay_thuong":
        thuong = random.choice(["🎉 Trúng 10K!", "🎁 Vé miễn phí!", "💎 VIP 1 ngày!", "🔥 Trúng 50K!"])
        await query.message.reply_text(f"🎰 {thuong}", reply_markup=main_keyboard())
    else:
        await query.message.reply_text(f"📊 Tổng icon: {len(icons)}", reply_markup=main_keyboard())

async def save_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.entities:
        return
    new_count = 0
    for e in update.message.entities:
        if e.type == MessageEntity.CUSTOM_EMOJI:
            cid = str(e.custom_emoji_id)
            if cid not in reverse_icons:
                name = f"icon_{len(icons)+1}"
                icons[name] = cid
                reverse_icons[cid] = name
                new_count += 1
    if new_count:
        save_icons()

def main():
    if not BOT_TOKEN:
        print("❌ THIẾU BOT_TOKEN")
        return
    print("🚀 Đang chạy bot polling - fix Python 3.14")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xemicon", xemicon))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), save_icon))
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
