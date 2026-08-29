import logging, os, base64, json
from datetime import time, datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN", "") 
if not BOT_TOKEN: BOT_TOKEN = "8835894291:AAGFaumezRa9baMMlEispiCVxa7VQjFeAz4"
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
            with open(LOGO_PATH, "wb") as f:
                f.write(base64.b64decode(LOGO_B64))
        except Exception as e:
            logging.warning(f"ensure_logo failed: {e}")

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Vào Nhóm Kín", url=PRIVATE_GROUP_LINK),
         InlineKeyboardButton("💬 Liên hệ Ad", url=LINK_LIEN_HE_AD)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="quay_thuong")]
    ])

def add_logo_to_image(image_path):
    try:
        from PIL import Image
        ensure_logo()
        base = Image.open(image_path).convert("RGBA")
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            # Resize logo = 18% chiều rộng ảnh
            w = int(base.width * 0.18)
            h = int(logo.height * (w / logo.width))
            logo = logo.resize((w, h))
            # Đặt góc dưới phải, cách lề 20px
            pos = (base.width - w - 20, base.height - h - 20)
            base.paste(logo, pos, logo)
        out_path = "temp_with_logo.jpg"
        base.convert("RGB").save(out_path, "JPEG", quality=92)
        return out_path
    except Exception as e:
        logging.warning(f"add_logo failed: {e}")
        return image_path

def get_bai_hom_nay(loai="kenh"):
    """
    loai = 'kenh' hoặc 'nhom_kin'
    Mỗi loại có kho riêng: lich_1_tuan/kenh và lich_1_tuan/nhom_kin
    File đặt tên: bai_1.jpg ... bai_7.jpg hoặc kenh_bai_1.jpg...
    Trả về đường dẫn file theo thứ trong tuần (VN UTC+7)
    """
    try:
        now_vn = datetime.utcnow() + timedelta(hours=7)
        thu = now_vn.weekday()  # 0=Mon, 6=Sun
        idx = thu + 1  # 1..7

        if loai == "kenh":
            folder = KENH_FOLDER
            candidates = [
                os.path.join(folder, f"kenh_bai_{idx}.jpg"),
                os.path.join(folder, f"bai_{idx}.jpg"),
                os.path.join(folder, f"{idx}.jpg"),
            ]
        else:
            folder = NHOM_KIN_FOLDER
            candidates = [
                os.path.join(folder, f"nhom_bai_{idx}.jpg"),
                os.path.join(folder, f"bai_{idx}.jpg"),
                os.path.join(folder, f"{idx}.jpg"),
            ]

        for p in candidates:
            if os.path.exists(p):
                return p

        # fallback: lấy file mới nhất trong folder
        if os.path.exists(folder):
            jpgs = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png"))]
            if jpgs:
                jpgs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                return jpgs[0]

        # fallback cuối cùng về file chung cũ
        if os.path.exists(IMAGE_PATH):
            return IMAGE_PATH

        return None
    except Exception as e:
        logging.warning(f"get_bai_hom_nay error: {e}")
        return None

async def dang_bai_20h(context: ContextTypes.DEFAULT_TYPE):
    """Đăng bài KÊNH - dùng KENH_FOLDER và CHANNEL_ID - 20h VN = 13h UTC"""
    try:
        img_path = get_bai_hom_nay(loai="kenh")
        if not img_path or not os.path.exists(img_path):
            await context.bot.send_message(chat_id=ADMIN_ID, text="⚠️ [KENH] Không tìm thấy ảnh hôm nay trong lich_1_tuan/kenh")
            return

        final_img = add_logo_to_image(img_path)
        caption = (
            "🔥 BÀI TỐI NAY 20H 🔥\n"
            "Kèo xịn BCR đã lên! Vào nhóm kín để lấy link sớm nhất nhé 👇"
        )
        with open(final_img, "rb") as photo:
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption,
                reply_markup=get_main_keyboard()
            )
        if final_img != img_path and os.path.exists(final_img) and "temp_with_logo" in final_img:
            os.remove(final_img)

        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ Đã đăng KÊNH: {img_path} -> CHANNEL_ID")
    except Exception as e:
        logging.warning(f"dang_bai_20h lỗi: {e}")
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Lỗi đăng KÊNH: {e}")
        except:
            pass

async def dang_bai_nhom_kin_20h(context: ContextTypes.DEFAULT_TYPE):
    """Đăng bài NHÓM KÍN - dùng NHOM_KIN_FOLDER và GROUP_ID - 20h05 VN = 13h05 UTC"""
    try:
        img_path = get_bai_hom_nay(loai="nhom_kin")
        if not img_path or not os.path.exists(img_path):
            await context.bot.send_message(chat_id=ADMIN_ID, text="⚠️ [NHÓM KÍN] Không tìm thấy ảnh hôm nay trong lich_1_tuan/nhom_kin")
            return

        final_img = add_logo_to_image(img_path)
        caption = (
            "🔒 BÀI TỐI NAY NHÓM KÍN 20H05 🔒\n"
            "Chỉ thành viên nhóm kín mới thấy bài này. Full HD không che 😎"
        )
        with open(final_img, "rb") as photo:
            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=photo,
                caption=caption
            )
        if final_img != img_path and os.path.exists(final_img) and "temp_with_logo" in final_img:
            os.remove(final_img)

        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ Đã đăng NHÓM KÍN: {img_path} -> GROUP_ID")
    except Exception as e:
        logging.warning(f"dang_bai_nhom_kin_20h lỗi: {e}")
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Lỗi đăng NHÓM KÍN: {e}")
        except:
            pass

async def bao_cao_cuoi_ngay(context: ContextTypes.DEFAULT_TYPE):
    try:
        now_vn = datetime.utcnow() + timedelta(hours=7)
        text = (
            f"📊 BÁO CÁO NGÀY {now_vn.strftime('%d/%m/%Y')}\n"
            f"• Kênh: {len(os.listdir(KENH_FOLDER)) if os.path.exists(KENH_FOLDER) else 0} file\n"
            f"• Nhóm kín: {len(os.listdir(NHOM_KIN_FOLDER)) if os.path.exists(NHOM_KIN_FOLDER) else 0} file\n"
            f"• Invite data: {len(invite_data)} user"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        logging.warning(f"bao_cao error: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"Xin chào {user.first_name}! 👋\n\n"
        f"Bot BCR đã tách Kênh & Nhóm Kín thành 2 kho riêng:\n"
        f"• 📢 Kênh: lich_1_tuan/kenh/\n"
        f"• 🔒 Nhóm kín: lich_1_tuan/nhom_kin/\n\n"
        f"Gửi ảnh kèm caption kenh_bai_1 hoặc nhom_bai_1 để up lịch.\n"
        f"Bot sẽ đăng tự động 20h (kênh) và 20h05 (nhóm kín) giờ VN."
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        try:
            await update.message.reply_text(
                f"Chào mừng {member.first_name} đã vào nhóm kín BCR! 🎉\nNhớ đọc ghim nhé!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Kênh chính", url="https://t.me/+PMp4CC-Q0XczOThl")]])
            )
        except Exception as e:
            logging.warning(f"chao error: {e}")

async def auto_reply_tu_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    txt = update.message.text.lower()
    if "link" in txt or "vào" in txt or "nhóm" in txt:
        await update.message.reply_text("Link nhóm kín đây bạn ơi 👇", reply_markup=get_main_keyboard())

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Dùng: /ban <user_id>")
        return
    try:
        uid = int(context.args[0])
        await context.bot.ban_chat_member(chat_id=GROUP_ID, user_id=uid)
        await update.message.reply_text(f"Đã ban {uid}")
    except Exception as e:
        await update.message.reply_text(f"Lỗi ban: {e}")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not invite_data:
        await update.message.reply_text("Chưa có dữ liệu mời.")
        return
    sorted_inv = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    msg = "🏆 TOP MỜI BẠN BÈ:\n"
    for i, (uid, count) in enumerate(sorted_inv, 1):
        msg += f"{i}. {uid}: {count} bạn\n"
    await update.message.reply_text(msg)

async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận ảnh từ admin và tự tách kho theo caption"""
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.photo:
        return

    caption = (update.message.caption or "").lower().strip()
    photo = update.message.photo[-1]

    try:
        # Xác định loại bài theo caption - FIX CHÍNH CHỐNG ĐĂNG TRÙNG
        if caption.startswith("kenh_bai_") or "kenh" in caption:
            folder = KENH_FOLDER
            loai = "KÊNH"
            # parse số bài: kenh_bai_1 -> bai_1.jpg hoặc giữ nguyên tên
            if "kenh_bai_" in caption:
                try:
                    num = caption.split("kenh_bai_")[1].split()[0].split(".")[0]
                    filename = f"kenh_bai_{num}.jpg"
                except:
                    filename = f"kenh_bai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            else:
                filename = f"kenh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        elif caption.startswith("nhom_bai_") or "nhom" in caption:
            folder = NHOM_KIN_FOLDER
            loai = "NHÓM KÍN"
            if "nhom_bai_" in caption:
                try:
                    num = caption.split("nhom_bai_")[1].split()[0].split(".")[0]
                    filename = f"nhom_bai_{num}.jpg"
                except:
                    filename = f"nhom_bai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            else:
                filename = f"nhom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        else:
            # Không rõ loại -> hỏi lại
            await update.message.reply_text(
                "⚠️ Vui lòng gửi kèm caption:\n"
                "• kenh_bai_1 -> lưu vào lich_1_tuan/kenh/\n"
                "• nhom_bai_1 -> lưu vào lich_1_tuan/nhom_kin/"
            )
            return

        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, filename)
        new_file = await photo.get_file()
        await new_file.download_to_drive(file_path)

        await update.message.reply_text(
            f"✅ Đã lưu [{loai}]: {file_path}\n"
            f"Kho hiện tại: {len(os.listdir(folder))} file"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi lưu ảnh: {e}")

async def test_dang_bai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    loai = args[0] if args else "kenh"
    if loai == "kenh":
        await dang_bai_20h(context)
        await update.message.reply_text("Đã test đăng KÊNH")
    else:
        await dang_bai_nhom_kin_20h(context)
        await update.message.reply_text("Đã test đăng NHÓM KÍN")

async def setup_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    kenh_count = len(os.listdir(KENH_FOLDER)) if os.path.exists(KENH_FOLDER) else 0
    nhom_count = len(os.listdir(NHOM_KIN_FOLDER)) if os.path.exists(NHOM_KIN_FOLDER) else 0
    await update.message.reply_text(
        f"📅 LỊCH HIỆN TẠI:\n"
        f"• lich_1_tuan/kenh: {kenh_count} file\n"
        f"• lich_1_tuan/nhom_kin: {nhom_count} file\n\n"
        f"Gửi ảnh với caption kenh_bai_1..7 và nhom_bai_1..7 để setup 1 tuần."
    )

async def xem_lich_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = "📂 CHI TIẾT KHO:\n\n"
    if os.path.exists(KENH_FOLDER):
        msg += f"📢 KÊNH ({KENH_FOLDER}):\n" + "\n".join(os.listdir(KENH_FOLDER)[:20]) + "\n\n"
    if os.path.exists(NHOM_KIN_FOLDER):
        msg += f"🔒 NHÓM KÍN ({NHOM_KIN_FOLDER}):\n" + "\n".join(os.listdir(NHOM_KIN_FOLDER)[:20])
    if len(msg) > 4000:
        msg = msg[:4000] + "..."
    await update.message.reply_text(msg or "Kho trống")

async def quay_thuong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    import random
    thuong = random.choice(["Chúc bạn may mắn lần sau!", "Bạn trúng 1 slot VIP!", "Tặng bạn code giảm 10%!", "Bạn trúng 1 tháng VIP BCR!"])
    await query.edit_message_text(f"🎁 KẾT QUẢ: {thuong}", reply_markup=get_main_keyboard())

def main():
    ensure_logo()
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("testdang", test_dang_bai_command))
    app.add_handler(CommandHandler("setuplich", setup_lich_command))
    app.add_handler(CommandHandler("xemlich", xem_lich_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, chao_thanh_vien_moi))
    app.add_handler(MessageHandler(filters.PHOTO, nhan_anh_moi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply_tu_dong))
    app.add_handler(CallbackQueryHandler(quay_thuong, pattern="quay_thuong"))
    app.add_handler(ChatMemberHandler(lambda u, c: None, ChatMemberHandler.CHAT_MEMBER))

    # FIX QUAN TRỌNG: TÁCH 2 JOB RIÊNG - CHỐNG ĐĂNG TRÙNG
    # 20h VN = 13h UTC đăng KÊNH
    app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))
    # 20h05 VN = 13h05 UTC đăng NHÓM KÍN
    app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))
    # Báo cáo cuối ngày 23h VN = 16h UTC
    app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=16, minute=0, second=0))

    print("Bot BCR đã tách kênh & nhóm kín - Đang chạy...")
    print(f"Kênh folder: {KENH_FOLDER}")
    print(f"Nhóm kín folder: {NHOM_KIN_FOLDER}")
    app.run_polling()

if __name__ == "__main__":
    main()
