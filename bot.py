import os, json, base64, logging, asyncio
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
from telegram.error import Conflict

# QUAN TRONG: Xoa token cung o dong nay di, chi dung bien moi truong thoi
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = -1001939368073
CHANNEL_ID = -1003098909518
PRIVATE_GROUP_LINK = "https://t.me/+PG4CC_QQKxZOTHl"
LINK_LIEN_HE_AD = "https://t.me/RWDNOTES"
ADMIN_ID = 8812690546

FILE_ICON = "premium_icons.json"

# --- LOAD ICON CU ---
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

# --- LENH /xemicon ---
async def xemicon(update: Update, context):
    if not icons:
        await update.message.reply_text("Chua co icon nao!")
        return
    # Lay 5 con dau de test
    list_ids = list(icons.values())[:5]
    text = "  " * len(list_ids)  # ky tu gia
    entities = []
    for i, cid in enumerate(list_ids):
        entities.append(MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)))
    
    await update.message.reply_text(
        f"Tong {len(icons)} icon. Test 5 con dau:\n{text}",
        entities=entities
    )

# --- LENH /layid ---
async def layid(update: Update, context):
    save_icons()
    if os.path.exists(FILE_ICON):
        await update.message.reply_document(
            document=open(FILE_ICON, "rb"),
            caption=f"Da co roi! Tong {len(icons)} icon! Go /xemicon"
        )
    else:
        await update.message.reply_text("Chua co file!")

# --- DOAN QUAN TRONG: TU DONG LUU ICON MOI VA GUI LAI ICON XIN ---
# Day la doan My tim khong thay vi truoc My dung reply_text thuong
# Doan nay se khac phuc loi "bot van dang icon thuong"
async def handle_premium(update: Update, context):
    if not update.message or not update.message.entities:
        return
    
    new_count = 0
    ids_in_message = []

    for e in update.message.entities:
        if e.type == MessageEntity.CUSTOM_EMOJI:
            cid = e.custom_emoji_id
            ids_in_message.append(cid)
            if str(cid) not in reverse_icons:
                new_key = f"icon_{len(icons)+1}"
                icons[new_key] = str(cid)
                reverse_icons[str(cid)] = new_key
                new_count += 1
    
    if new_count > 0:
        save_icons()
        await update.message.reply_text(f"Da luu {new_count} icon moi! Tong {len(icons)}!")

    # Neu muon bot tu dong gui lai bang icon xin (khong phai icon thuong) thi bo comment 5 dong duoi
    # if ids_in_message:
    #     text = "  " * len(ids_in_message)
    #     entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(ids_in_message)]
    #     await update.message.reply_text(text, entities=entities)

# --- CAC HANDLER CU CUA MY GIU NGUYEN O DUOI DAY ---
# My copy cac ham cu nhu start, doc cau bcr... vao duoi day

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("xemicon", xemicon))
    app.add_handler(CommandHandler("layid", layid))
    app.add_handler(CommandHandler("lay_id_icon", layid))
    # Handler nay phai de cuoi cung
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), handle_premium))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
