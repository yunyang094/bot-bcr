import logging, os, base64, json
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
import asyncio
BOT_TOKEN = os.getenv("BOT_TOKEN","")
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
    if not os.path.exists(LOGO_PATH):
        try:
            if LOGO_B64:
                data = base64.b64decode(LOGO_B64)
                with open(LOGO_PATH, "wb") as f:
                    f.write(data)
        except:
            pass

def get_main_keyboard(bot_username=None):
    link_bot = f"https://t.me/{bot_username}?start=thongke" if bot_username else "https://t.me/doccaubcr_bot?start=thongke"
    nut_1 = InlineKeyboardButton("VAO NHOM KIN VIP", url=PRIVATE_GROUP_LINK)
    nut_2 = InlineKeyboardButton("LIEN HE AD", url=LINK_LIEN_HE_AD)
    nut_3 = InlineKeyboardButton("XEM THONG KE", url=link_bot)
    nut_4 = InlineKeyboardButton("QUAY THUONG", callback_data="quay_thuong")
    return InlineKeyboardMarkup([[nut_1], [nut_2, nut_3], [nut_4]])

def add_logo_to_image(image_path):
    ensure_logo()
    try:
        from PIL import Image, ImageDraw
        if not os.path.exists(image_path) or not os.path.exists(LOGO_PATH):
            return
        board = Image.open(image_path).convert("RGBA")
        W, H = board.size
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_size_corner = int(W * 0.18)
        logo_corner = logo.resize((logo_size_corner, logo_size_corner), Image.LANCZOS)
        bg_size = int(logo_size_corner * 1.15)
        bg = Image.new("RGBA", (bg_size, bg_size), (0,0,0,0))
        draw = ImageDraw.Draw(bg)
        draw.ellipse([0,0,bg_size-1,bg_size-1], fill=(255,255,255,230), outline=(0,0,0,200), width=2)
        x = W - bg_size - int(H*0.04)
        y = H - bg_size - int(H*0.04)
        board.alpha_composite(bg, (x, y))
        lx = x + (bg_size - logo_size_corner)//2
        ly = y + (bg_size - logo_size_corner)//2
        board.alpha_composite(logo_corner, (lx, ly))
        logo_size_center = int(W * 0.38)
        logo_center = logo.resize((logo_size_center, logo_size_center), Image.LANCZOS)
        alpha = logo_center.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.32))
        logo_center.putalpha(alpha)
        cx = (W - logo_size_center)//2
        cy = (H - logo_size_center)//2
        board.alpha_composite(logo_center, (cx, cy))
        board.convert("RGB").save(image_path, "JPEG", quality=92)
    except Exception as e:
        print(f"Loi logo: {e}")

def get_bai_hom_nay(loai="kenh"):
    if loai == "nhom_kin":
        folder = NHOM_KIN_FOLDER
    else:
        folder = KENH_FOLDER
    os.makedirs(folder, exist_ok=True)
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    index = None
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r", encoding="utf-8") as f:
                lich = json.load(f)
                start_date = datetime.fromisoformat(lich.get("start_date"))
                days_passed = (datetime.now() - start_date).days
                index = days_passed % 7 + 1
        except:
            pass
    if index and 1 <= index <= 7:
        img = os.path.join(folder, f"bai_{index}.jpg")
        cap = os.path.join(folder, f"bai_{index}.txt")
        if os.path.exists(img):
            return img, cap
        img_old = os.path.join(SCHEDULE_FOLDER, f"bai_{index}.jpg")
        cap_old = os.path.join(SCHEDULE_FOLDER, f"bai_{index}.txt")
        if os.path.exists(img_old):
            return img_old, cap_old
    weekday = datetime.now().weekday() + 1
    img = os.path.join(folder, f"bai_{weekday}.jpg")
    cap = os.path.join(folder, f"bai_{weekday}.txt")
    if os.path.exists(img):
        return img, cap
    img_old = os.path.join(SCHEDULE_FOLDER, f"bai_{weekday}.jpg")
    cap_old = os.path.join(SCHEDULE_FOLDER, f"bai_{weekday}.txt")
    if os.path.exists(img_old):
        return img_old, cap_old
    if loai == "nhom_kin":
        return os.path.join(folder, "bai_1.jpg"), os.path.join(folder, "bai_1.txt")
    return IMAGE_PATH, "caption.txt"

async def dang_bai_20h(context):
    ensure_logo()
    image_path_tuan, caption_path_tuan = get_bai_hom_nay("kenh")
    caption = None
    if os.path.exists(caption_path_tuan):
        with open(caption_path_tuan, "r", encoding="utf-8") as f:
            caption = f.read()
    elif os.path.exists("caption.txt"):
        with open("caption.txt", "r", encoding="utf-8") as f:
            caption = f.read()
    if not caption:
        caption = f"[BAI {datetime.now().strftime('%d/%m')} - Co bet] Anh sau live 30p."
    if os.path.exists(image_path_tuan):
        add_logo_to_image(image_path_tuan)
        image_to_send = image_path_tuan
    else:
        image_to_send = IMAGE_PATH
        if os.path.exists(IMAGE_PATH):
            add_logo_to_image(IMAGE_PATH)
    try:
        kb = get_main_keyboard(context.bot.username)
        if os.path.exists(image_to_send):
            with open(image_to_send, "rb") as photo:
                msg = await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption, reply_markup=kb)
                try:
                    await context.bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=msg.message_id, disable_notification=True)
                except:
                    pass
        else:
            msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=kb)
            try:
                await context.bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=msg.message_id, disable_notification=True)
            except:
                pass
        print(f"Da dang KENH: {image_to_send}")
    except Exception as e:
        print(f"Loi dang kenh: {e}")

async def dang_bai_nhom_kin_20h(context):
    ensure_logo()
    image_path_tuan, caption_path_tuan = get_bai_hom_nay("nhom_kin")
    caption = None
    if os.path.exists(caption_path_tuan):
        with open(caption_path_tuan, "r", encoding="utf-8") as f:
            caption = f.read()
    if not caption:
        caption = f"CAU VIP NHOM KIN - {datetime.now().strftime('%d/%m')}"
    try:
        if os.path.exists(image_path_tuan):
            add_logo_to_image(image_path_tuan)
            with open(image_path_tuan, "rb") as photo:
                await context.bot.send_photo(chat_id=GROUP_ID, photo=photo, caption=caption)
        else:
            await context.bot.send_message(chat_id=GROUP_ID, text=caption)
        print(f"Da dang NHOM KIN: {image_path_tuan}")
    except Exception as e:
        print(f"Loi dang nhom kin: {e}")

async def bao_cao_cuoi_ngay(context):
    try:
        if not invite_data:
            return
        top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:5]
        lines = []
        for uid, count in top_sorted:
            lines.append(f"- ID {uid}: {count} nguoi")
        text = "BAO CAO CUOI NGAY - TOP MOI:\n" + "\n".join(lines)
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        print(f"Loi bao cao: {e}")

async def start_command(update, context):
    user_id = update.effective_user.id
    if context.args and context.args[0] == "thongke":
        if user_id!= ADMIN_ID:
            await update.message.reply_text("Ban khong co quyen!")
            return
        if not invite_data:
            await update.message.reply_text("Chua co ai moi!")
            return
        top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
        lines = [f"- ID {uid}: {count}" for uid, count in top_sorted]
        text = "THONG KE:\n" + "\n".join(lines)
        await update.message.reply_text(text)
        return
    if context.args and len(context.args) > 0:
        try:
            inviter_id = int(context.args[0])
            if inviter_id!= user_id:
                invite_data[inviter_id] = invite_data.get(inviter_id, 0) + 1
        except:
            pass
    await update.message.reply_text(f"Chao mung {update.effective_user.first_name}! Nhan nut ben duoi de vao nhom kin VIP!", reply_markup=get_main_keyboard(context.bot.username))

async def chao_thanh_vien_moi(update, context):
    try:
        if update.chat_member.chat.id!= GROUP_ID:
            return
        old_status = update.chat_member.old_chat_member.status
        new_status = update.chat_member.new_chat_member.status
        if old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            user = update.chat_member.new_chat_member.user
            await context.bot.send_message(chat_id=GROUP_ID, text=f"Chao mung {user.first_name} da vao nhom kin VIP!", reply_markup=get_main_keyboard(context.bot.username))
    except:
        pass

async def auto_reply_tu_dong(update, context):
    try:
        if update.effective_chat.id!= GROUP_ID:
            return
        text = update.message.text.lower() if update.message.text else ""
        if any(k in text for k in ["bet", "cau", "chot", "bcr", "bai"]):
            await update.message.reply_text("My phan tich bet that + bay Ho doi o nhom rieng roi nha!", reply_markup=get_main_keyboard(context.bot.username))
    except:
        pass

async def ban_command(update, context):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Dung: /ban <user_id>")
        return
    try:
        user_id = int(context.args[0])
        await context.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user_id)
        await update.message.reply_text(f"Da ban {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Loi ban: {e}")

async def top_command(update, context):
    if not invite_data:
        await update.message.reply_text("Chua co ai moi!")
        return
    top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    lines = [f"- ID {uid}: {count} nguoi" for uid, count in top_sorted]
    text = "TOP MOI BAN BE:\n" + "\n".join(lines)
    await update.message.reply_text(text)

async def nhan_anh_moi(update, context):
    if update.effective_user.id!= ADMIN_ID:
        return
    ensure_logo()
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    photo_file = await update.message.photo[-1].get_file()
    caption_text = update.message.caption or ""
    cap_lower = caption_text.lower()
    loai = "kenh"
    if "nhom" in cap_lower or "kin" in cap_lower:
        loai = "nhom_kin"
    for i in range(1, 8):
        if f"bai_{i}" in cap_lower or f"bai {i}" in cap_lower:
            if loai == "nhom_kin":
                path = os.path.join(NHOM_KIN_FOLDER, f"bai_{i}.jpg")
                cap_path = os.path.join(NHOM_KIN_FOLDER, f"bai_{i}.txt")
                folder_name = "NHOM KIN"
            else:
                path = os.path.join(KENH_FOLDER, f"bai_{i}.jpg")
                cap_path = os.path.join(KENH_FOLDER, f"bai_{i}.txt")
                folder_name = "KENH"
            await photo_file.download_to_drive(path)
            add_logo_to_image(path)
            clean_cap = caption_text
            for tag in [f"kenh_bai_{i}", f"nhom_bai_{i}", f"nhom_kin_bai_{i}", f"bai_{i}", f"bai {i}"]:
                clean_cap = clean_cap.replace(tag, "").replace(tag.upper(), "")
            clean_cap = clean_cap.strip()
            if clean_cap:
                with open(cap_path, "w", encoding="utf-8") as f:
                    f.write(clean_cap)
            await update.message.reply_text(f"Da luu vao {folder_name}: bai_{i}.jpg + logo BCR!", reply_markup=get_main_keyboard(context.bot.username))
            return
    await photo_file.download_to_drive(IMAGE_PATH)
    if update.message.caption:
        with open("caption.txt", "w", encoding="utf-8") as f:
            f.write(update.message.caption)
    add_logo_to_image(IMAGE_PATH)
    await update.message.reply_text(f"OK My! Da luu anh hom nay!", reply_markup=get_main_keyboard(context.bot.username))

async def test_dang_bai_command(update, context):
    if update.effective_user.id!= ADMIN_ID:
        return
    await update.message.reply_text("Dang test dang bai 20h...")
    try:
        await dang_bai_20h(context)
        await asyncio.sleep(2)
        await dang_bai_nhom_kin_20h(context)
        await update.message.reply_text("Test xong! Kenh va Nhom kin da dang RIENG!")
    except Exception as e:
        await update.message.reply_text(f"Loi test: {e}")

async def setup_lich_command(update, context):
    if update.effective_user.id!= ADMIN_ID:
        return
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    start_date = datetime.now().isoformat()
    lich = {"start_date": start_date, "link_nhom": PRIVATE_GROUP_LINK}
    with open(LICH_FILE, "w", encoding="utf-8") as f:
        json.dump(lich, f, ensure_ascii=False, indent=2)
    ds = []
    for i in range(1, 8):
        img_k = os.path.join(KENH_FOLDER, f"bai_{i}.jpg")
        img_n = os.path.join(NHOM_KIN_FOLDER, f"bai_{i}.jpg")
        ds.append(f"Ngay {i}: Kenh {'OK' if os.path.exists(img_k) else 'NO'} | Nhom kin {'OK' if os.path.exists(img_n) else 'NO'}")
    await update.message.reply_text("LICH TACH RIENG:\n\n" + "\n".join(ds))

async def xem_lich_command(update, context):
    if update.effective_user.id!= ADMIN_ID:
        return
    ds = []
    for i in range(1, 8):
        img_k = os.path.join(KENH_FOLDER, f"bai_{i}.jpg")
        img_n = os.path.join(NHOM_KIN_FOLDER, f"bai_{i}.jpg")
        ds.append(f"Ngay {i}: Kenh {'OK' if os.path.exists(img_k) else 'NO'} | Nhom kin {'OK' if os.path.exists(img_n) else 'NO'}")
    await update.message.reply_text("LICH HIEN TAI:\n\n" + "\n".join(ds))

async def quay_thuong(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Chuc mung! Vao nhom kin de nhan thuong:", reply_markup=get_main_keyboard(context.bot.username))

def main():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except Exception as e:
        print(f"Loop fix: {e}")
    ensure_logo()
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    print(f"Kenh folder: {KENH_FOLDER}")
    print(f"Nhom kin folder: {NHOM_KIN_FOLDER}")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("setup_lich", setup_lich_command))
    app.add_handler(CommandHandler("xem_lich", xem_lich_command))
    app.add_handler(CommandHandler("testdangbai", test_dang_bai_command))
    app.add_handler(CallbackQueryHandler(quay_thuong, pattern="quay_thuong"))
    app.add_handler(ChatMemberHandler(chao_thanh_vien_moi, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(user_id=ADMIN_ID), nhan_anh_moi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, auto_reply_tu_dong))
    if app.job_queue:
        app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))
        app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))
        app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=16, minute=0, second=0))
    print("Bot BCR da tach kenh & nhom kin - Dang chay!")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
