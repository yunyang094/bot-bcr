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
    BOT_TOKEN = "8835894291:" + "AAGFaumezRa9baMMlEispiCVxa7VQjFeAz4"
GROUP_ID = -1003939505873
CHANNEL_ID = -1003980680518
PRIVATE_GROUP_LINK = "https://t.me/+PMp4CC-Q0XczOThl"  # LINK MỚI NHẤT
LINK_LIEN_HE_AD = "https://t.me/RNBNOTES"
ADMIN_ID = 8632660546
IMAGE_PATH = "bai_toi_nay_20h.jpg"
LOGO_PATH = "logo_bcr_transparent.png"
LICH_FILE = "lich_1_tuan.json"
SCHEDULE_FOLDER = "lich_1_tuan"

LOGO_B64 = ""  # sẽ tự tạo nếu chưa có, dùng base64 cũ của My

invite_data = {}
logging.basicConfig(level=logging.WARNING)

def ensure_logo():
    if not os.path.exists(LOGO_PATH):
        try:
            if LOGO_B64:
                data = base64.b64decode(LOGO_B64)
                with open(LOGO_PATH, "wb") as f:
                    f.write(data)
                print("Da tao logo BCR tu dong!")
        except Exception as e:
            print(f"Loi tao logo: {e}")

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
        if not os.path.exists(image_path) or not os.path.exists(LOGO_PATH):
            return
        board = Image.open(image_path).convert("RGBA")
        W, H = board.size
        logo = Image.open(LOGO_PATH).convert("RGBA")

        # 1. LOGO GÓC PHẢI DƯỚI
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

        # 2. LOGO GIỮA - watermark mờ chống copy
        logo_size_center = int(W * 0.38)
        logo_center = logo.resize((logo_size_center, logo_size_center), Image.LANCZOS)
        alpha = logo_center.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.32))
        logo_center.putalpha(alpha)
        cx = (W - logo_size_center)//2
        cy = (H - logo_size_center)//2
        board.alpha_composite(logo_center, (cx, cy))

        board.convert("RGB").save(image_path, "JPEG", quality=92)
        print("Da dong 2 logo BCR - goc + giua!")
    except Exception as e:
        print(f"Loi logo: {e}")

def get_bai_hom_nay():
    """Lấy bài của hôm nay theo lịch 1 tuần"""
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    
    # Kiểm tra file lịch
    ngay_hom_nay = datetime.now().day  # hoặc dùng file lich_1_tuan.json để tính
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r", encoding="utf-8") as f:
                lich = json.load(f)
                start_date = datetime.fromisoformat(lich.get("start_date"))
                days_passed = (datetime.now() - start_date).days
                index = days_passed % 7 + 1  # 1-7
                if 1 <= index <= 7:
                    img_path = os.path.join(SCHEDULE_FOLDER, f"bai_{index}.jpg")
                    cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{index}.txt")
                    if os.path.exists(img_path):
                        return img_path, cap_path
        except:
            pass
    
    # Fallback: kiểm tra theo thứ tự ngày
    # Nếu My up 7 ảnh tên bai_1.jpg -> bai_7.jpg trong folder lich_1_tuan
    for i in range(1, 8):
        img_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
        cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.txt")
        # Ưu tiên bài chưa đăng, đơn giản là check file image mặc định hôm nay
        # My sẽ hiểu: hôm nay đăng bai_1, mai bai_2...
        # Logic đơn giản: dùng ngày trong tuần
        weekday = datetime.now().weekday() + 1  # 1-7 (T2-CN)
        if weekday == i and os.path.exists(img_path):
            return img_path, cap_path

    # Cuối cùng: dùng file mặc định
    return IMAGE_PATH, "caption.txt"

async def dang_bai_20h(context: ContextTypes.DEFAULT_TYPE):
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    
    # LẤY BÀI THEO LỊCH 1 TUẦN
    image_path_tuan, caption_path_tuan = get_bai_hom_nay()
    
    # Đọc caption
    caption = None
    if os.path.exists(caption_path_tuan):
        with open(caption_path_tuan, "r", encoding="utf-8") as f:
            caption = f.read()
    elif os.path.exists("caption.txt"):
        with open("caption.txt", "r", encoding="utf-8") as f:
            caption = f.read()
    
    if not caption:
        caption = """[BÀI %s - Có bệt] Ảnh sau live 30p.

Bead có bệt P 4 tay, có 2 Hổ đỏ đôi. Đây có phải bệt thật không? My phân tích bệt thật (>=4 ô) + bẫy Hổ đôi ở nhóm riêng rồi. Thống kê quá khứ. 18+.""" % datetime.now().strftime("%d/%m")

    # Nếu là bài trong lịch tuần thì gắn logo luôn
    if os.path.exists(image_path_tuan) and SCHEDULE_FOLDER in image_path_tuan:
        add_logo_to_image(image_path_tuan)
        image_to_send = image_path_tuan
    else:
        if os.path.exists(IMAGE_PATH):
            add_logo_to_image(IMAGE_PATH)
        image_to_send = IMAGE_PATH

    try:
        kb = get_main_keyboard(context.bot.username)
        if os.path.exists(image_to_send):
            with open(image_to_send, "rb") as photo:
                msg = await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption, reply_markup=kb)
        else:
            msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=kb)
        try:
            await context.bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=msg.message_id, disable_notification=True)
        except:
            pass
        print(f"Da dang bai 20h thanh cong! - File: {image_to_send}")
    except Exception as e:
        print(f"Loi dang bai: {e}")

async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_member.status == ChatMemberStatus.MEMBER:
        new_user = update.chat_member.new_chat_member.user
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Chào {new_user.mention_html()} đã vào nhóm của My! Nhớ đọc ghim nhé!", parse_mode="HTML", reply_markup=get_main_keyboard(context.bot.username))
        inviter = update.chat_member.from_user
        if inviter.id != new_user.id:
            invite_data[inviter.id] = invite_data.get(inviter.id, 0) + 1

async def auto_reply_tu_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.lower()
    if "t.me/" in text and PRIVATE_GROUP_LINK not in text:
        try:
            await update.message.delete()
            return
        except:
            pass
    if "cau" in text:
        await update.message.reply_text("My gửi cầu chi tiết trong nhóm kín rồi:", reply_markup=get_main_keyboard(context.bot.username))
    elif "nhom" in text or "link" in text:
        await update.message.reply_text(f"Link nhóm kín đây: {PRIVATE_GROUP_LINK}", reply_markup=get_main_keyboard(context.bot.username))

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and update.message.reply_to_message:
        await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id
    if args and args[0].startswith("ref_"):
        inviter_id = int(args[0].replace("ref_", ""))
        invite_data[inviter_id] = invite_data.get(inviter_id, 0) + 1
        await update.message.reply_text(f"Cảm ơn bạn! Link nhóm kín: {PRIVATE_GROUP_LINK}", reply_markup=get_main_keyboard(context.bot.username))
    else:
        my_ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        if user_id == ADMIN_ID:
            await update.message.reply_text(f"Chào Admin My! Bot 1 FILE - SETUP 1 TUẦN + Logo BCR đã chạy!\nLink mới: {my_ref_link}\n\nGửi 7 ảnh + 7 caption vào folder lich_1_tuan/bai_1.jpg -> bai_7.jpg là bot tự đăng 7 ngày!", reply_markup=get_main_keyboard(context.bot.username))
        else:
            await update.message.reply_text(f"Link mời riêng của bạn:\n{my_ref_link}\nĐiểm: {invite_data.get(user_id, 0)}", reply_markup=get_main_keyboard(context.bot.username))

async def dang_bai_nhom_kin_20h(context: ContextTypes.DEFAULT_TYPE):
    """Job riêng cho nhóm kín - đăng cầu VIP chi tiết"""
    from datetime import datetime
    # Lấy bài chi tiết cho nhóm kín
    # Nếu My muốn khác với kênh, My để file nhom_kin_bai_1.txt...
    date_str = datetime.now().strftime("%d/%m/%Y")
    # Đọc file nhóm kín nếu có
    import os
    nhom_kin_caption = None
    # Thử đọc file nhom_kin riêng
    for i in range(1,8):
        path = f"lich_1_tuan/nhom_kin_bai_{i}.txt"
        if os.path.exists(path):
            # Dùng theo ngày
            weekday = datetime.now().weekday() + 1
            if weekday == i:
                with open(path, "r", encoding="utf-8") as f:
                    nhom_kin_caption = f.read()
                break
    
    if not nhom_kin_caption:
        # Fallback dùng chung caption kênh nhưng thêm chi tiết
        nhom_kin_caption = f"""CẦU VIP 20H - NHÓM KÍN - {date_str}
My chốt chi tiết ở đây!

(Kênh chỉ đăng ảnh sau live 30p, nhóm kín mới chốt)

18+ Quản lý vốn nhé!
Link kênh: {PRIVATE_GROUP_LINK}
"""
    
    try:
        await context.bot.send_message(chat_id=PRIVATE_GROUP_ID, text=nhom_kin_caption)
        print(f"[JOB] Đã đăng bài 20h vào NHÓM KÍN {PRIVATE_GROUP_ID}")
    except Exception as e:
        print(f"Lỗi đăng nhóm kín: {e}")

async def bao_cao_cuoi_ngay(context: ContextTypes.DEFAULT_TYPE):
    total_new = sum(invite_data.values())
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Báo cáo hôm nay: {total_new} người mới")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not invite_data:
        await update.message.reply_text("Chưa có ai mời!")
        return
    top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "TOP MỜI BẠN BÈ:\n" + "\n".join([f"- ID {uid}: {count} người" for uid, count in top_sorted])
    await update.message.reply_text(text)

async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    
    # Nếu My gửi ảnh thường -> lưu làm bài hôm nay
    photo_file = await update.message.photo[-1].get_file()
    
    # Kiểm tra xem My đang setup lịch tuần không
    # Nếu caption có "bai_1", "bai_2"... thì lưu vào lịch tuần
    caption_text = update.message.caption or ""
    if "bai_" in caption_text.lower():
        # Ví dụ caption: "bai_3" thì lưu thành bai_3.jpg
        for i in range(1, 8):
            if f"bai_{i}" in caption_text.lower():
                path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.jpg")
                cap_path = os.path.join(SCHEDULE_FOLDER, f"bai_{i}.txt")
                await photo_file.download_to_drive(path)
                add_logo_to_image(path)
                # Lưu caption riêng (bỏ chữ bai_x đi)
                clean_cap = caption_text.replace(f"bai_{i}", "").replace(f"Bai_{i}", "").strip()
                if clean_cap:
                    with open(cap_path, "w", encoding="utf-8") as f:
                        f.write(clean_cap)
                await update.message.reply_text(f"✅ Đã lưu vào LỊCH TUẦN: bai_{i}.jpg + logo BCR!\nBot sẽ tự đăng ngày thứ {i}!", reply_markup=get_main_keyboard(context.bot.username))
                return
    
    # Mặc định: lưu bài hôm nay
    await photo_file.download_to_drive(IMAGE_PATH)
    if update.message.caption:
        with open("caption.txt", "w", encoding="utf-8") as f:
            f.write(update.message.caption)
    add_logo_to_image(IMAGE_PATH)
    await update.message.reply_text(f"✅ OK My! Đã lưu ảnh hôm nay + LOGO CHUẨN BCR! Tối 20h bot sẽ đăng!", reply_markup=get_main_keyboard(context.bot.username))

async def setup_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /setup_lich để bắt đầu lịch 1 tuần mới"""
    if update.effective_user.id != ADMIN_ID:
        return
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
    
    text = f"""📅 ĐÃ SETUP LỊCH 1 TUẦN MỚI!

Bắt đầu từ: {datetime.now().strftime('%d/%m/%Y')}
Link nhóm mới: {PRIVATE_GROUP_LINK}

Danh sách bài:
{chr(10).join(ds_bai)}

Cách up bài cho 1 tuần:
1. Gửi ảnh kèm caption "bai_1 + nội dung" -> bot lưu bài thứ 2
2. Tương tự "bai_2", "bai_3"... đến "bai_7"
3. Hoặc up file trực tiếp vào folder lich_1_tuan/

Bot sẽ tự đăng 20h mỗi ngày theo thứ tự!
"""
    await update.message.reply_text(text)

async def xem_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
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
    # FIX Python 3.14 event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except:
        pass
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("setup_lich", setup_lich_command))
    app.add_handler(CommandHandler("xem_lich", xem_lich_command))
    app.add_handler(CommandHandler("testdangbai", lambda u,c: c.job_queue.run_once(lambda ctx: dang_bai_20h(ctx), 1) or u.message.reply_text("Dang test dang bai 20h...")))
    app.add_handler(CallbackQueryHandler(quay_thuong, pattern="quay_thuong"))
    app.add_handler(ChatMemberHandler(chao_thanh_vien_moi, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(user_id=ADMIN_ID), nhan_anh_moi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, auto_reply_tu_dong))
    if app.job_queue:
        app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))  # 13h UTC = 20h VN
        app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))  # Đăng nhóm kín sau kênh 5 phút
        app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=16, minute=0, second=0))
    print("Bot 1 FILE DUY NHAT - SETUP 1 TUAN - FULL chuc nang + Logo BCR - Dang 20h VN - OK!")
    print(f"Link nhom moi: {PRIVATE_GROUP_LINK}")
    print("My chi can gui anh moi cho bot qua Telegram la xong!")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, close_loop=False)

if __name__ == "__main__":
    main()
