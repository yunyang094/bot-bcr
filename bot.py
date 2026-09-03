import os, json, random
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/+xxxx")  # Link nhom kin
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")  # ID admin
ADMIN_LINK = os.getenv("ADMIN_LINK", f"tg://user?id={ADMIN_ID}")
FILE_ICON = "premium_icons.json"
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or ""

# ICON
try:
    icons = json.load(open(FILE_ICON, "r", encoding="utf-8")) if os.path.exists(FILE_ICON) else {}
except:
    icons = {}
reverse_icons = {str(v): k for k, v in icons.items()}
def save_icons():
    json.dump(icons, open(FILE_ICON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ========== CAC NUT ==========
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Nhóm Kín", url=GROUP_LINK),
         InlineKeyboardButton("👤 Admin", url=ADMIN_LINK)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="quay_thuong"),
         InlineKeyboardButton("📊 Thống Kê", callback_data="thong_ke")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== CHAO THANH VIEN MOI ==========
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
                await update.message.reply_text(f"Chào mừng {name} đến với nhóm!\nBấm nút bên dưới nhé!", reply_markup=main_keyboard())

# ========== CAC LENH ==========
async def start(update: Update, context):
    await update.message.reply_text(
        f"Bot BCR Full Tính Năng đang chạy!\n{len(icons)} icon premium\nCó đủ: Chào TV mới, Nút nhóm kín, Admin, Quay thưởng, Thống kê, Đăng 20:00",
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

# ========== NUT QUAY THUONG + THONG KE ==========
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "quay_thuong":
        thuong = random.choice(["🎉 Chúc mừng bạn trúng 10K!", "🎁 Bạn trúng 1 vé miễn phí!", "😢 Chúc bạn may mắn lần sau!", "💎 Bạn trúng VIP 1 ngày!", "🔥 Bạn trúng 50K!"])
        await query.message.reply_text(f"🎰 KẾT QUẢ QUAY THƯỞNG\n\n{thuong}", reply_markup=main_keyboard())
    
    elif query.data == "thong_ke":
        try:
            chat = await context.bot.get_chat(query.message.chat_id)
            count = await context.bot.get_chat_member_count(query.message.chat_id)
            await query.message.reply_text(f"📊 THỐNG KÊ NHÓM\n\n👥 Thành viên: {count}\n📛 Tên nhóm: {chat.title}\n🆔 ID: {chat.id}\n✨ Icon đã lưu: {len(icons)}", reply_markup=main_keyboard())
        except:
            await query.message.reply_text(f"📊 THỐNG KÊ\n\n✨ Icon đã lưu: {len(icons)}\nBot đang hoạt động bình thường!", reply_markup=main_keyboard())

# ========== DANG KENH 20:00 ==========
async def post_20h_kenh(context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL_ID:
        return
    icon_id = list(icons.values())[0] if icons else None
    if icon_id:
        text = "  TAI LIEU 20:00\nTai lieu hom nay da len! Bam nut duoi de vao nhom kin!"
        ent = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=str(icon_id))]
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text, entities=ent, reply_markup=main_keyboard())
    else:
        await context.bot.send_message(chat_id=CHANNEL_ID, text="TAI LIEU 20:00\nTai lieu hom nay da len!", reply_markup=main_keyboard())

# ========== LUU ICON ==========
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
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Lenh
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("xemicon", xemicon))
    
    # Chao TV moi
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # Nut bam
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Luu icon
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), save_icon))
    
    # Auto 20:00 kenh
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    app.job_queue.run_daily(post_20h_kenh, time=time(20, 0, tzinfo=tz))
    
    if WEBHOOK_URL:
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path="webhook", webhook_url=f"{WEBHOOK_URL.rstrip('/')}/webhook", drop_pending_updates=True)
    else:
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
import os, json, random
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/+xxxx")  # Link nhom kin
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")  # ID admin
ADMIN_LINK = os.getenv("ADMIN_LINK", f"tg://user?id={ADMIN_ID}")
FILE_ICON = "premium_icons.json"
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or ""

# ICON
try:
    icons = json.load(open(FILE_ICON, "r", encoding="utf-8")) if os.path.exists(FILE_ICON) else {}
except:
    icons = {}
reverse_icons = {str(v): k for k, v in icons.items()}
def save_icons():
    json.dump(icons, open(FILE_ICON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ========== CAC NUT ==========
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Nhóm Kín", url=GROUP_LINK),
         InlineKeyboardButton("👤 Admin", url=ADMIN_LINK)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="quay_thuong"),
         InlineKeyboardButton("📊 Thống Kê", callback_data="thong_ke")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== CHAO THANH VIEN MOI ==========
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
                await update.message.reply_text(f"Chào mừng {name} đến với nhóm!\nBấm nút bên dưới nhé!", reply_markup=main_keyboard())

# ========== CAC LENH ==========
async def start(update: Update, context):
    await update.message.reply_text(
        f"Bot BCR Full Tính Năng đang chạy!\n{len(icons)} icon premium\nCó đủ: Chào TV mới, Nút nhóm kín, Admin, Quay thưởng, Thống kê, Đăng 20:00",
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

# ========== NUT QUAY THUONG + THONG KE ==========
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "quay_thuong":
        thuong = random.choice(["🎉 Chúc mừng bạn trúng 10K!", "🎁 Bạn trúng 1 vé miễn phí!", "😢 Chúc bạn may mắn lần sau!", "💎 Bạn trúng VIP 1 ngày!", "🔥 Bạn trúng 50K!"])
        await query.message.reply_text(f"🎰 KẾT QUẢ QUAY THƯỞNG\n\n{thuong}", reply_markup=main_keyboard())
    
    elif query.data == "thong_ke":
        try:
            chat = await context.bot.get_chat(query.message.chat_id)
            count = await context.bot.get_chat_member_count(query.message.chat_id)
            await query.message.reply_text(f"📊 THỐNG KÊ NHÓM\n\n👥 Thành viên: {count}\n📛 Tên nhóm: {chat.title}\n🆔 ID: {chat.id}\n✨ Icon đã lưu: {len(icons)}", reply_markup=main_keyboard())
        except:
            await query.message.reply_text(f"📊 THỐNG KÊ\n\n✨ Icon đã lưu: {len(icons)}\nBot đang hoạt động bình thường!", reply_markup=main_keyboard())

# ========== DANG KENH 20:00 ==========
async def post_20h_kenh(context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL_ID:
        return
    icon_id = list(icons.values())[0] if icons else None
    if icon_id:
        text = "  TAI LIEU 20:00\nTai lieu hom nay da len! Bam nut duoi de vao nhom kin!"
        ent = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=str(icon_id))]
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text, entities=ent, reply_markup=main_keyboard())
    else:
        await context.bot.send_message(chat_id=CHANNEL_ID, text="TAI LIEU 20:00\nTai lieu hom nay da len!", reply_markup=main_keyboard())

# ========== LUU ICON ==========
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
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Lenh
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("xemicon", xemicon))
    
    # Chao TV moi
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # Nut bam
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Luu icon
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), save_icon))
    
    # Auto 20:00 kenh
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    app.job_queue.run_daily(post_20h_kenh, time=time(20, 0, tzinfo=tz))
    
    if WEBHOOK_URL:
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path="webhook", webhook_url=f"{WEBHOOK_URL.rstrip('/')}/webhook", drop_pending_updates=True)
    else:
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
import os, json, random
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/+xxxx")  # Link nhom kin
ADMIN_ID = os.getenv("ADMIN_ID", "123456789")  # ID admin
ADMIN_LINK = os.getenv("ADMIN_LINK", f"tg://user?id={ADMIN_ID}")
FILE_ICON = "premium_icons.json"
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or ""

# ICON
try:
    icons = json.load(open(FILE_ICON, "r", encoding="utf-8")) if os.path.exists(FILE_ICON) else {}
except:
    icons = {}
reverse_icons = {str(v): k for k, v in icons.items()}
def save_icons():
    json.dump(icons, open(FILE_ICON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ========== CAC NUT ==========
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Nhóm Kín", url=GROUP_LINK),
         InlineKeyboardButton("👤 Admin", url=ADMIN_LINK)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="quay_thuong"),
         InlineKeyboardButton("📊 Thống Kê", callback_data="thong_ke")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== CHAO THANH VIEN MOI ==========
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
                await update.message.reply_text(f"Chào mừng {name} đến với nhóm!\nBấm nút bên dưới nhé!", reply_markup=main_keyboard())

# ========== CAC LENH ==========
async def start(update: Update, context):
    await update.message.reply_text(
        f"Bot BCR Full Tính Năng đang chạy!\n{len(icons)} icon premium\nCó đủ: Chào TV mới, Nút nhóm kín, Admin, Quay thưởng, Thống kê, Đăng 20:00",
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

# ========== NUT QUAY THUONG + THONG KE ==========
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "quay_thuong":
        thuong = random.choice(["🎉 Chúc mừng bạn trúng 10K!", "🎁 Bạn trúng 1 vé miễn phí!", "😢 Chúc bạn may mắn lần sau!", "💎 Bạn trúng VIP 1 ngày!", "🔥 Bạn trúng 50K!"])
        await query.message.reply_text(f"🎰 KẾT QUẢ QUAY THƯỞNG\n\n{thuong}", reply_markup=main_keyboard())
    
    elif query.data == "thong_ke":
        try:
            chat = await context.bot.get_chat(query.message.chat_id)
            count = await context.bot.get_chat_member_count(query.message.chat_id)
            await query.message.reply_text(f"📊 THỐNG KÊ NHÓM\n\n👥 Thành viên: {count}\n📛 Tên nhóm: {chat.title}\n🆔 ID: {chat.id}\n✨ Icon đã lưu: {len(icons)}", reply_markup=main_keyboard())
        except:
            await query.message.reply_text(f"📊 THỐNG KÊ\n\n✨ Icon đã lưu: {len(icons)}\nBot đang hoạt động bình thường!", reply_markup=main_keyboard())

# ========== DANG KENH 20:00 ==========
async def post_20h_kenh(context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL_ID:
        return
    icon_id = list(icons.values())[0] if icons else None
    if icon_id:
        text = "  TAI LIEU 20:00\nTai lieu hom nay da len! Bam nut duoi de vao nhom kin!"
        ent = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=str(icon_id))]
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text, entities=ent, reply_markup=main_keyboard())
    else:
        await context.bot.send_message(chat_id=CHANNEL_ID, text="TAI LIEU 20:00\nTai lieu hom nay da len!", reply_markup=main_keyboard())

# ========== LUU ICON ==========
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
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Lenh
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("xemicon", xemicon))
    
    # Chao TV moi
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    
    # Nut bam
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Luu icon
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), save_icon))
    
    # Auto 20:00 kenh
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    app.job_queue.run_daily(post_20h_kenh, time=time(20, 0, tzinfo=tz))
    
    if WEBHOOK_URL:
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path="webhook", webhook_url=f"{WEBHOOK_URL.rstrip('/')}/webhook", drop_pending_updates=True)
    else:
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
