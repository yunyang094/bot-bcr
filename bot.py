import logging
import os
import base64
import json
from datetime import time, datetime, timedelta
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
        except: pass

def get_main_keyboard(bot_username=None):
    link_bot = f"https://t.me/{bot_username}?start=thongke" if bot_username else "https://t.me/doccaubcr_bot?start=thongke"
    nut_1 = InlineKeyboardButton("🔥 VÀO NHÓM KÍN VIP", url=PRIVATE_GROUP_LINK)
    nut_2 = InlineKeyboardButton("💬 LIÊN HỆ AD", url=LINK_LIEN_HE_AD)
    nut_3 = InlineKeyboardButton("📊 XEM THỐNG KÊ", url=link_bot)
    nut_4 = InlineKeyboardButton("🎁 QUAY THƯỞNG", callback_data="quay_thuong")
    return InlineKeyboardMarkup([[nut_1], [nut_2, nut_3], [nut_4]])

def add_logo_to_image(image_path):
    ensure_logo()
    try:
        from PIL import Image, ImageDraw
        if not os.path.exists(image_path) or not os.path.exists(LOGO_PATH): return
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

def get_bai_hom_nay():
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r", encoding="utf-8") as f:
                lich = json.load(f)
                start_date = datetime.fromisoformat(lich.get("start_date"))
                days_passed = (datetime.now() - start_date).days
                if days_passed < 0: days_passed = 0
                index = days_passed % 7 + 1
                img_path = os.path.join(SCHEDULE_FOLDER, f"bai_{index}.jpg")
                cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{index}.txt")
                if os.path.exists(img_path):
                    return img_path, cap_path
        except: pass
    for i in range(1, 8):
        img_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
        cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.txt")
        if os.path.exists(img_path):
            return img_path, cap_path
    return IMAGE_PATH, "caption.txt"

async def dang_bai_20h(context: ContextTypes.DEFAULT_TYPE):
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    image_path_tuan, caption_path_tuan = get_bai_hom_nay()
    caption = None
    if os.path.exists(caption_path_tuan):
        with open(caption_path_tuan, "r", encoding="utf-8") as f:
            caption = f.read()
    elif os.path.exists("caption.txt"):
        with open("caption.txt", "r", encoding="utf-8") as f:
            caption = f.read()
    if not caption:
        caption = f"[BÀI {datetime.now().strftime('%d/%m')} - Có bệt] Ảnh sau live 30p. Bead có bệt P 4 tay, có 2 Hổ đỏ đôi. Đây có phải bệt thật không? My phân tích bệt thật (>=4 ô) + bẫy Hổ đôi ở nhóm riêng rồi. Thống kê quá khứ. 18+."
    image_to_send = image_path_tuan if os.path.exists(image_path_tuan) and SCHEDULE_FOLDER in image_path_tuan else IMAGE_PATH
    if os.path.exists(image_to_send):
        add_logo_to_image(image_to_send)
    try:
        kb = get_main_keyboard(context.bot.username)
        if os.path.exists(image_to_send):
            with open(image_to_send, "rb") as photo:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption, reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=kb)
    except Exception as e:
        print(f"Loi dang KENH: {e}")

async def dang_bai_nhom_kin_20h(context: ContextTypes.DEFAULT_TYPE):
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    image_path_tuan, caption_path_tuan = get_bai_hom_nay()
    caption = None
    if os.path.exists(caption_path_tuan):
        with open(caption_path_tuan, "r", encoding="utf-8") as f:
            caption = f.read()
    elif os.path.exists("caption.txt"):
        with open("caption.txt", "r", encoding="utf-8") as f:
            caption = f.read()
    if not caption:
        caption = f"[NHÓM KÍN - BÀI {datetime.now().strftime('%d/%m')}] Phân tích chi tiết..."
    image_to_send = image_path_tuan if os.path.exists(image_path_tuan) and SCHEDULE_FOLDER in image_path_tuan else IMAGE_PATH
    if os.path.exists(image_to_send):
        add_logo_to_image(image_to_send)
    try:
        kb = get_main_keyboard(context.bot.username)
        if os.path.exists(image_to_send):
            with open(image_to_send, "rb") as photo:
                await context.bot.send_photo(chat_id=GROUP_ID, photo=photo, caption=caption, reply_markup=kb)
        else:
            await context.bot.send_message(chat_id=GROUP_ID, text=caption, reply_markup=kb)
    except Exception as e:
        print(f"Loi dang NHOM KIN: {e}")

async def bao_cao_cuoi_ngay(context: ContextTypes.DEFAULT_TYPE):
    try:
        if not invite_data: return
        top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:5]
        text = "📊 BÁO CÁO CUỐI NGÀY:\n" + "\n".join([f"- ID {uid}: {count} người" for uid, count in top_sorted])
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    except: pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0] == "thongke":
        user_id = update.effective_user.id
        count = invite_data.get(user_id, 0)
        await update.message.reply_text(f"Bạn đã mời được {count} người!")
        return
    await update.message.reply_text("Chào mừng! Nhấn nút bên dưới để vào nhóm kín:", reply_markup=get_main_keyboard(context.bot.username))

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Dùng: /ban <user_id>")
        return
    try:
        user_id = int(context.args[0])
        await context.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user_id)
        await update.message.reply_text(f"Đã ban {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Lỗi ban: {e}")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not invite_data:
        await update.message.reply_text("Chưa có ai mời!")
        return
    top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "TOP MỜI BẠN BÈ:\n" + "\n".join([f"- ID {uid}: {count} người" for uid, count in top_sorted])
    await update.message.reply_text(text)

async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for member in update.chat_member.new_chat_members:
            if member.id == context.bot.id: continue
            inviter = update.chat_member.from_user
            if inviter:
                invite_data[inviter.id] = invite_data.get(inviter.id, 0) + 1
            await context.bot.send_message(chat_id=GROUP_ID, text=f"Chào mừng {member.mention_html()} đã vào nhóm! Nhớ đọc ghim nhé!", parse_mode="HTML")
    except Exception as e:
        print(f"Loi chao: {e}")

async def auto_reply_tu_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.lower()
        if "bcr" in text or "cầu" in text or "bệt" in text:
            await update.message.reply_text("Bạn hỏi về cầu à? Vào nhóm kín để xem phân tích chi tiết nhé!", reply_markup=get_main_keyboard(context.bot.username))
    except: pass

async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    photo_file = await update.message.photo[-1].get_file()
    caption_text = update.message.caption or ""
    low = caption_text.lower().replace("-", "_")
    if "bai_" in low:
        for i in range(1, 8):
            if f"bai_{i}" in low:
                path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
                cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.txt")
                await photo_file.download_to_drive(path)
                add_logo_to_image(path)
                clean_cap = caption_text
                for kw in [f"bai_{i}", f"bai-{i}", f"Bai_{i}", f"Bai-{i}", f"bai_{i}".upper()]:
                    clean_cap = clean_cap.replace(kw, "")
                clean_cap = clean_cap.strip()
                if clean_cap:
                    with open(cap_path, "w", encoding="utf-8") as f:
                        f.write(clean_cap)
                await update.message.reply_text(f"✅ Đã lưu vào LỊCH TUẦN: bai_{i}.jpg + logo BCR!\nBot sẽ tự đăng ngày thứ {i}!", reply_markup=get_main_keyboard(context.bot.username))
                return
    await photo_file.download_to_drive(IMAGE_PATH)
    if update.message.caption:
        with open("caption.txt", "w", encoding="utf-8") as f:
            f.write(update.message.caption)
    add_logo_to_image(IMAGE_PATH)
    await update.message.reply_text(f"✅ OK My! Đã lưu ảnh hôm nay + LOGO CHUẨN BCR! Tối 20h bot sẽ đăng!", reply_markup=get_main_keyboard(context.bot.username))

async def test_dang_bai_command(update, context):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("Đang test đăng bài 20h...")
    try:
        await dang_bai_20h(context)
        await update.message.reply_text("✅ Test xong! Kiểm tra kênh đi My! Bài đã đăng theo lịch 7 ngày!")
    except Exception as e:
        await update.message.reply_text(f"Lỗi test: {e}")

async def setup_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    start_date = datetime.now().isoformat()
    lich = {"start_date": start_date, "link_nhom": PRIVATE_GROUP_LINK}
    with open(LICH_FILE, "w", encoding="utf-8") as f:
        json.dump(lich, f, ensure_ascii=False, indent=2)
    ds_bai = []
    for i in range(1, 8):
        img = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
        status = "✅" if os.path.exists(img) else "❌"
        ds_bai.append(f"{status} bai_{i}.jpg")
    text = f"📅 ĐÃ SETUP LỊCH 1 TUẦN MỚI - FIX BUG!\n\nBắt đầu từ: {datetime.now().strftime('%d/%m/%Y')}\nLink nhóm mới: {PRIVATE_GROUP_LINK}\n\nDanh sách bài:\n{chr(10).join(ds_bai)}\n\n✅ FIX: Tính từ ngày setup, không tính theo thứ nữa! Hôm setup = bài 1, Mai = bài 2...\nNhận cả bai-1 và bai_1!"
    await update.message.reply_text(text)

async def xem_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    ds = []
    for i in range(1, 8):
        img = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
        cap = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.txt")
        has_img = "✅ Ảnh" if os.path.exists(img) else "❌ Chưa có ảnh"
        has_cap = "✅ Caption" if os.path.exists(cap) else "❌ Chưa có caption"
        ds.append(f"Ngày {i}: {has_img} | {has_cap}")
    await update.message.reply_text("📅 LỊCH 1 TUẦN HIỆN TẠI:\n\n" + "\n".join(ds) + f"\n\nLink nhóm: {PRIVATE_GROUP_LINK}")

async def quay_thuong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🎉 Chúc mừng! Vào nhóm kín để nhận thưởng:", reply_markup=get_main_keyboard(context.bot.username))

def main():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except: pass
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
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
    print("Bot 1 FILE DUY NHAT - SETUP 1 TUAN - FULL chuc nang + Logo BCR - Dang 20h VN - OK!")
    print(f"Link nhom moi: {PRIVATE_GROUP_LINK}")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, close_loop=False)

if __name__ == "__main__":
    main()
