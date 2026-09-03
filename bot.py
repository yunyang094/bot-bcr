import os, json, base64, logging, asyncio
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
from telegram.error import Conflict

# --- CAU HINH ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = -1001939368073
CHANNEL_ID = -1003098909518
PRIVATE_GROUP_LINK = "https://t.me/+PG4CC_QQKxZOTHl"
LINK_LIEN_HE_AD = "https://t.me/RWDNOTES"
ADMIN_ID = 8812690546
IMAGE_PATH = "Dai_ly_Boy_200k.jpg"
LOGO_PATH = "logo_bcr_transparent.png"
LICH_FILE = "lich_thi_dau.json"
SCHEDULE_FOLDER = "lichthidau"
FILE_ICON = "premium_icons.json"

logging.basicConfig(level=logging.INFO)

# --- LOAD ICON ---
if os.path.exists(FILE_ICON):
    try:
        with open(FILE_ICON, "r", encoding="utf-8") as f:
            icons = json.load(f)
    except:
        icons = {}
else:
    icons = {}
reverse_icons = {str(v): k for k, v in icons.items()}
def save_icons():
    with open(FILE_ICON, "w", encoding="utf-8") as f:
        json.dump(icons, f, indent=2, ensure_ascii=False)

# --- LENH /start ---
async def start(update: Update, context):
    await update.message.reply_text(
        f"🤖 Bot BCR VIP đang chạy!\n"
        f"📦 Tổng {len(icons)} icon xịn\n"
        f"📅 Gõ /lich để xem lịch\n"
        f"💎 Gõ /xemicon để test icon"
    )

# --- LENH /xemicon ---
async def xemicon(update: Update, context):
    if not icons:
        await update.message.reply_text("Chưa có icon nào! Hãy gửi icon premium vào nhóm để bot lưu!")
        return
    list_ids = list(icons.values())[:5]
    text = "  " * len(list_ids)
    entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
    await update.message.reply_text(f"Tổng {len(icons)} icon. Test 5 con đầu:\n{text}", entities=entities)

# --- LENH /layid ---
async def layid(update: Update, context):
    save_icons()
    if os.path.exists(FILE_ICON):
        await update.message.reply_document(open(FILE_ICON, "rb"), caption=f"Đã có rồi! Tổng {len(icons)} icon!")
    else:
        await update.message.reply_text("Chưa có file!")

# --- LENH /lich - KHOI PHUC DAY DU ---
async def lich(update: Update, context):
    # 1. Thu doc file lich_thi_dau.json
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            msg = "📅 **LỊCH THI ĐẤU HÔM NAY**\n\n"
            if isinstance(data, list):
                for item in data[:20]:
                    msg += f"• {item}\n"
            else:
                msg += json.dumps(data, ensure_ascii=False, indent=2)[:3500]
            await update.message.reply_text(msg)
            return
        except Exception as e:
            await update.message.reply_text(f"Lỗi đọc {LICH_FILE}: {e}")

    # 2. Neu khong co file, doc thu muc lichthidau
    if os.path.exists(SCHEDULE_FOLDER):
        files = os.listdir(SCHEDULE_FOLDER)
        if files:
            msg = f"📁 Trong thư mục {SCHEDULE_FOLDER} có {len(files)} file:\n" + "\n".join([f"• {x}" for x in files[:20]])
            await update.message.reply_text(msg)
            return
    
    await update.message.reply_text("Chưa có file lịch thi đấu! Hãy up file lich_thi_dau.json lên Github!")

# --- XU LY TIN NHAN BCR TRONG NHOM (giu lai logic cu) ---
async def handle_bcr_message(update: Update, context):
    # Chi xu ly tin nhan trong nhom chinh
    if update.effective_chat.id != GROUP_ID:
        return
    text = update.message.text or ""
    # Day la cho xu ly doc cau BCR cua My, My co the them logic vao day
    # Hien tai Bao de trong de khong loi
    if "bcr" in text.lower() or "cầu" in text.lower():
        pass

# --- FIX LOI ICON THUONG - TU DONG LUU ICON XIN ---
async def handle_premium(update: Update, context):
    if not update.message or not update.message.entities:
        return
    new_count = 0
    for e in update.message.entities:
        if e.type == MessageEntity.CUSTOM_EMOJI:
            cid = str(e.custom_emoji_id)
            if cid not in reverse_icons:
                new_key = f"icon_{len(icons)+1}"
                icons[new_key] = cid
                reverse_icons[cid] = new_key
                new_count += 1
    if new_count > 0:
        save_icons()
        logging.info(f"Da luu {new_count} icon moi")

# --- MAIN DAY DU TU DAU DEN CUOI ---
def main():
    if not BOT_TOKEN:
        print("THIEU BOT_TOKEN!")
        return
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xemicon", xemicon))
    app.add_handler(CommandHandler("layid", layid))
    app.add_handler(CommandHandler("lay_id_icon", layid))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("lichthidau", lich))
    
    # Tin nhan thuong trong nhom (doc cau BCR)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bcr_message))
    
    # Icon phai de cuoi cung
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), handle_premium))

    print("Bot BCR FULL dang chay... gom ca lich va icon!")
    app.run_polling()

if __name__ == "__main__":
    main()
