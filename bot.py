import os, json, random, asyncio
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# FIX LOI EVENT LOOP TREN PYTHON 3.14 - RENDER
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/+xxxx")
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")
ADMIN_LINK = os.getenv("ADMIN_LINK", f"tg://user?id={ADMIN_ID}")
FILE_ICON = "premium_icons.json"
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = (os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").strip()

# ICON
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

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            name = member.first_name
            icon_id = list(icons.values())[0] if icons else None
            if icon_id:
                text = f"  Chào mừng {name} đến với nhóm!\nBấm nút bên dưới để tham gia nhé!"
                ent = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=str(icon_id))]
                await update.message.reply_text(text, entities=ent, reply_markup=main_keyboard())
            else:
                await update.message.reply_text(f"Chào mừng {name} đến với nhóm!", reply_markup=main_keyboard())

async def start(update: Update, context):
    await update.message.reply_text(
        f"✅ Bot BCR đang chạy - Không xung đột!\n{len(icons)} icon premium\n20:00 tự đăng kênh",
        reply_markup=main_keyboard()
    )

async def lich(update: Update, context):
    await update.message.reply_text("Lịch 20:00 sẽ tự đăng lên kênh!", reply_markup=main_keyboard())

async def xemicon(update: Update, context):
    if not icons:
        await update.message.reply_text("Chưa có icon! Gửi icon premium vào group đi!")
        return
    list_ids = list(icons.values())[:5]
    text = "  " * len(list_ids)
    entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
    await update.message.reply_text(f"Test {len(icons)} icon:\n{text}", entities=entities, reply_markup=main_keyboard())

async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "quay_thuong":
        thuong = random.choice(["🎉 Chúc mừng bạn trúng 10K!", "🎁 Bạn trúng 1 vé miễn phí!", "😢 Chúc bạn may mắn lần sau!", "💎 Bạn trúng VIP 1 ngày!", "🔥 Bạn trúng 50K!"])
        await query.message.reply_text(f"🎰 KẾT QUẢ QUAY THƯỞNG\n\n{thuong}", reply_markup=main_keyboard())
    elif query.data == "thong_ke":
        try:
            count = await context.bot.get_chat_member_count(query.message.chat_id)
            chat = await context.bot.get_chat(query.message.chat_id)
            await query.message.reply_text(f"📊 THỐNG KÊ NHÓM\n\n👥 Thành viên: {count}\n📛 Tên: {chat.title}\n🆔 ID: {chat.id}\n✨ Icon: {len(icons)}", reply_markup=main_keyboard())
        except:
            await query.message.reply_text(f"📊 THỐNG KÊ\n\n✨ Icon đã lưu: {len(icons)}\nBot đang hoạt động!", reply_markup=main_keyboard())

async def post_20h_kenh(context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL_ID:
        return
    try:
        icon_id = list(icons.values())[0] if icons else None
        if icon_id:
            text = "  TAI LIEU 20:00\nTai lieu hom nay da len! Bam nut duoi de vao nhom kin!"
            ent = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=str(icon_id))]
            await context.bot.send_message(chat_id=CHANNEL_ID, text=text, entities=ent, reply_markup=main_keyboard())
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text="TAI LIEU 20:00\nTai lieu hom nay da len!", reply_markup=main_keyboard())
    except Exception as e:
        print(f"Loi dang 20h: {e}")

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

def main():
    if not BOT_TOKEN:
        print("THIEU BOT_TOKEN!")
        return
    print(f"PORT={PORT} WEBHOOK_URL={WEBHOOK_URL}")
    
    # Fix loop lan nua cho chac
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("xemicon", xemicon))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), save_icon))
    
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    try:
        app.job_queue.run_daily(post_20h_kenh, time=time(20, 0, tzinfo=tz))
    except Exception as e:
        print(f"Khong chay duoc job_queue: {e}")

    if WEBHOOK_URL:
        clean_url = WEBHOOK_URL.rstrip("/")
        full_webhook = f"{clean_url}/webhook"
        print(f"Chay WEBHOOK mode: {full_webhook}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=full_webhook,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    else:
        print("Khong co WEBHOOK_URL - chay POLLING")
        app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
