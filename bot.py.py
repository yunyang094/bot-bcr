import logging
import os
import json
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("CHUA SET BOT_TOKEN TRONG RENDER!")

GROUP_ID = -1003939505873
CHANNEL_ID = -1003980680518
PRIVATE_GROUP_LINK = "https://t.me/+PMp4CC-Q0XczOThl"
PRIVATE_GROUP_ID = -1003939505873
ADMIN_ID = 8632660546
IMAGE_PATH = "bai_toi_nay_20h.jpg"
LOGO_PATH = "logo_bcr_transparent.png"
LICH_FILE = "lich_1_tuan.json"
SCHEDULE_FOLDER = "lich_1_tuan"
invite_data = {}
logging.basicConfig(level=logging.WARNING)

def get_main_keyboard(bot_username=None):
    nut_1 = InlineKeyboardButton("VAO NHOM KIN VIP", url=PRIVATE_GROUP_LINK)
    nut_2 = InlineKeyboardButton("LIEN HE AD", url="https://t.me/RNBNOTES")
    return InlineKeyboardMarkup([[nut_1], [nut_2]])

def get_bai_hom_nay():
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    for i in range(1, 8):
        img_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
        cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.txt")
        weekday = datetime.now().weekday() + 1
        if weekday == i and os.path.exists(img_path):
            return img_path, cap_path
    return IMAGE_PATH, "caption.txt"

async def dang_bai_20h(context: ContextTypes.DEFAULT_TYPE):
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    image_path_tuan, caption_path_tuan = get_bai_hom_nay()
    caption = ""
    if os.path.exists(caption_path_tuan):
        with open(caption_path_tuan, "r", encoding="utf-8") as f:
            caption = f.read()
    if not caption:
        caption = "[BAI HOM NAY] Vao nhom kin xem 18+"
    try:
        kb = get_main_keyboard(context.bot.username)
        if os.path.exists(image_path_tuan):
            with open(image_path_tuan, "rb") as photo:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption, reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=kb)
    except Exception as e:
        print(f"Loi: {e}")

async def dang_bai_nhom_kin_20h(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=PRIVATE_GROUP_ID, text=f"CAU VIP 20H - {datetime.now().strftime('%d/%m/%Y')}")
    except Exception as e:
        print(f"Loi nhom kin: {e}")

async def bao_cao_cuoi_ngay(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Bao cao: {sum(invite_data.values())}")
    except:
        pass

async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.chat_member.new_chat_member.status == ChatMemberStatus.MEMBER:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Chao {update.chat_member.new_chat_member.user.mention_html()}!", parse_mode="HTML", reply_markup=get_main_keyboard())
    except:
        pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    my_ref_link = f"https://t.me/{context.bot.username}?start=ref_{update.effective_user.id}"
    await update.message.reply_text(f"Chao Admin My! Bot da chay!\n{my_ref_link}", reply_markup=get_main_keyboard())

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("TOP...")

async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(IMAGE_PATH)
    if update.message.caption:
        with open("caption.txt", "w", encoding="utf-8") as f:
            f.write(update.message.caption)
    await update.message.reply_text("Da luu!")

async def test_dang_bai_command(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("Dang test...")
    await dang_bai_20h(context)
    await update.message.reply_text("Xong!")

async def setup_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Da setup lich moi!")

async def xem_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lich 1 tuan...")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"LOI: {context.error}")

def main():
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("setup_lich", setup_lich_command))
    app.add_handler(CommandHandler("xem_lich", xem_lich_command))
    app.add_handler(CommandHandler("testdangbai", test_dang_bai_command))
    app.add_handler(ChatMemberHandler(chao_thanh_vien_moi, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(user_id=ADMIN_ID), nhan_anh_moi))
    if app.job_queue:
        app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))
        app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))
        app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=16, minute=0, second=0))
    print("Bot chay OK - Python 3.11.9 - Khong lo Token!")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
