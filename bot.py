import logging
import os
import base64
import json
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    BOT_TOKEN = "8835894291:AAGFaumezRa9baMMlEispiCVxa7VQjFeAz4"

GROUP_ID = -1003939505873
CHANNEL_ID = -1003980680518
PRIVATE_GROUP_LINK = "https://t.me/+PMp4CC-Q0XczOThl"
LINK_LIEN_HE_AD = "https://t.me/RNBNOTES"
ADMIN_ID = 8632660546
IMAGE_PATH = "bai_toi_nay_20h.jpg"
LOGO_PATH = "logo_bcr_transparent.png"
LICH_FILE = "lich_1_tuan.json"
SCHEDULE_FOLDER = "lich_1_tuan"
KENH_FOLDER = os.path.join(SCHEDULE_FOLDER, "kenh")
NHOM_KIN_FOLDER = os.path.join(SCHEDULE_FOLDER, "nhom_kin")
LOGO_B64 = ""
invite_data = {}
logging.basicConfig(level=logging.WARNING)


def ensure_logo():
    if LOGO_B64 and not os.path.exists(LOGO_PATH):
        try:
            data = base64.b64decode(LOGO_B64)
            with open(LOGO_PATH, "wb") as f:
                f.write(data)
        except Exception as e:
            logging.warning(f"Cannot decode logo: {e}")


def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Quay Thuong", callback_data="quay_thuong")],
        [InlineKeyboardButton("Xem Lich", callback_data="xem_lich"),
         InlineKeyboardButton("Top Moi", callback_data="top")],
        [InlineKeyboardButton("Lien He AD", url=LINK_LIEN_HE_AD),
         InlineKeyboardButton("Nhom Kin", url=PRIVATE_GROUP_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)


def add_logo_to_image(image_path):
    try:
        from PIL import Image
        if not os.path.exists(LOGO_PATH) or not os.path.exists(image_path):
            return image_path
        base = Image.open(image_path).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")
        w, h = base.size
        logo_size = int(w * 0.18)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        margin = int(w * 0.02)
        base.paste(logo, (w - logo_size - margin, h - logo_size - margin), logo)
        out_path = "output_" + os.path.basename(image_path)
        base.convert("RGB").save(out_path, "JPEG", quality=92)
        return out_path
    except Exception as e:
        logging.warning(f"add_logo failed: {e}")
        return image_path


def get_bai_hom_nay(loai="kenh"):
    folder = KENH_FOLDER if loai == "kenh" else NHOM_KIN_FOLDER
    try:
        if not os.path.exists(folder):
            return None
        today = datetime.now()
        weekday = today.weekday()
        map_day = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]
        day_name = map_day[weekday]
        candidates = [
            os.path.join(folder, f"{day_name}.json"),
            os.path.join(folder, f"{today.strftime('%Y-%m-%d')}.json"),
            os.path.join(SCHEDULE_FOLDER, LICH_FILE)
        ]
        for path in candidates:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if day_name in data:
                            return data[day_name]
                        if loai in data:
                            return data[loai]
                        return data
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
        return None
    except Exception as e:
        logging.warning(f"get_bai_hom_nay error: {e}")
        return None


async def dang_bai_20h(context: ContextTypes.DEFAULT_TYPE):
    try:
        bai = get_bai_hom_nay("kenh")
        if not bai:
            return
        caption = bai.get("caption", "Bai dang 20h hom nay")
        img = bai.get("image", IMAGE_PATH)
        final_img = add_logo_to_image(img) if os.path.exists(img) else None
        if final_img and os.path.exists(final_img):
            with open(final_img, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=caption,
                    reply_markup=get_main_keyboard()
                )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logging.warning(f"dang_bai_20h error: {e}")


async def dang_bai_nhom_kin_20h(context: ContextTypes.DEFAULT_TYPE):
    try:
        bai = get_bai_hom_nay("nhom_kin")
        if not bai:
            bai = get_bai_hom_nay("kenh")
        if not bai:
            return
        caption = bai.get("caption_nhom_kin", bai.get("caption", "Bai dang nhom kin 20h"))
        img = bai.get("image", IMAGE_PATH)
        final_img = add_logo_to_image(img) if os.path.exists(img) else None
        if final_img and os.path.exists(final_img):
            with open(final_img, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=GROUP_ID,
                    photo=photo,
                    caption=caption,
                    reply_markup=get_main_keyboard()
                )
        else:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=caption,
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logging.warning(f"dang_bai_nhom_kin_20h error: {e}")


async def bao_cao_cuoi_ngay(context: ContextTypes.DEFAULT_TYPE):
    try:
        top_list = []
        for user_id, count in sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]:
            top_list.append(f"{user_id}: {count} moi")
        if not top_list:
            text = "Bao cao cuoi ngay - TOP MOI:
Chua co du lieu moi hom nay."
        else:
            text = f"Bao cao cuoi ngay - TOP MOI:
" + "\n".join(top_list)
        await context.bot.send_message(chat_id=GROUP_ID, text=text)
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    except Exception as e:
        logging.warning(f"bao_cao_cuoi_ngay error: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        if user:
            invite_data[str(user.id)] = invite_data.get(str(user.id), 0)
        text = (
            f"Xin chao {user.first_name if user else 'ban'}!\n"
            f"Bot hoat dong on dinh.\n"
            f"Su dung menu ben duoi de thao tac."
        )
        await update.message.reply_text(text, reply_markup=get_main_keyboard())
    except Exception as e:
        logging.warning(f"start_command error: {e}")


async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for member in update.message.new_chat_members:
            text = (
                f"Chao mung {member.first_name} den voi nhom!\n"
                f"Vui long doc noi quy va lien he AD neu can ho tro.\n"
                f"Link lien he: {LINK_LIEN_HE_AD}"
            )
            await update.message.reply_text(text)
            if update.effective_user:
                inviter_id = str(update.effective_user.id)
                invite_data[inviter_id] = invite_data.get(inviter_id, 0) + 1
    except Exception as e:
        logging.warning(f"chao_thanh_vien_moi error: {e}")


async def auto_reply_tu_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return
        msg = update.message.text.lower()
        if "ad" in msg or "admin" in msg or "ho tro" in msg:
            await update.message.reply_text(
                f"Lien he AD tai day: {LINK_LIEN_HE_AD}",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logging.warning(f"auto_reply error: {e}")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        if not context.args or len(context.args) < 1:
            await update.message.reply_text("Dung: /ban <user_id>")
            return
        target = int(context.args[0])
        await context.bot.ban_chat_member(chat_id=GROUP_ID, user_id=target)
        await update.message.reply_text(f"Da ban {target}")
    except Exception as e:
        await update.message.reply_text(f"Loi ban: {e}")


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sorted_data = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
        if not sorted_data:
            await update.message.reply_text("Chua co du lieu top moi.")
            return
        lines = []
        for idx, (uid, cnt) in enumerate(sorted_data, 1):
            lines.append(f"{idx}. {uid} - {cnt} moi")
        text = "TOP moi nhieu nhat:\n" + "\n".join(lines)
        await update.message.reply_text(text)
    except Exception as e:
        logging.warning(f"top_command error: {e}")


async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("Chi admin moi duoc gui anh.")
            return
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive(IMAGE_PATH)
        await update.message.reply_text(f"Da luu anh moi: {IMAGE_PATH}")
    except Exception as e:
        await update.message.reply_text(f"Loi luu anh: {e}")


async def test_dang_bai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("Dang test dang bai 20h...")
    await dang_bai_20h(context)
    await dang_bai_nhom_kin_20h(context)
    await update.message.reply_text("Da test xong.")


async def setup_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        os.makedirs(KENH_FOLDER, exist_ok=True)
        os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
        await update.message.reply_text(
            f"Da tao thu muc:\n- {KENH_FOLDER}\n- {NHOM_KIN_FOLDER}\n"
            f"Dat file json theo ngay vao tung thu muc."
        )
    except Exception as e:
        await update.message.reply_text(f"Loi setup lich: {e}")


async def xem_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kenh = get_bai_hom_nay("kenh")
        nhom = get_bai_hom_nay("nhom_kin")
        msg = f"Lich hom nay:\nKENH: {json.dumps(kenh, ensure_ascii=False) if kenh else 'Chua co'}\n"
        msg += f"NHOM_KIN: {json.dumps(nhom, ensure_ascii=False) if nhom else 'Chua co'}"
        await update.message.reply_text(msg[:4000])
    except Exception as e:
        await update.message.reply_text(f"Loi xem lich: {e}")


async def quay_thuong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        try:
            user = query.from_user
            await query.edit_message_text(
                f"Chuc mung {user.first_name}! Ban da quay thuong thanh cong.\n"
                f"Lien he AD de nhan qua: {LINK_LIEN_HE_AD}",
                reply_markup=get_main_keyboard()
            )
        except Exception as e:
            logging.warning(f"quay_thuong error: {e}")


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ensure_logo()
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("testdangbai", test_dang_bai_command))
    app.add_handler(CommandHandler("setuplich", setup_lich_command))
    app.add_handler(CommandHandler("xemlich", xem_lich_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, chao_thanh_vien_moi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply_tu_dong))
    app.add_handler(MessageHandler(filters.PHOTO, nhan_anh_moi))
    app.add_handler(CallbackQueryHandler(quay_thuong, pattern="quay_thuong"))
    app.add_handler(CallbackQueryHandler(top_command, pattern="top"))
    app.job_queue.run_daily(dang_bai_20h, time=time(hour=20, minute=0))
    app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=20, minute=5))
    app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=23, minute=55))
    print("Bot dang chay... Kiem tra cu phap OK")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

