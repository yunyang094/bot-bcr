import os, json, base64, logging, asyncio
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ChatMemberHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatMemberStatus
from telegram.error import Conflict

BOT_TOKEN = os.getenv("BOT_TOKEN", "") or "8835894291:AAGFaumezRa9baMMlEispiCVxa7VQjFeAz4"
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

PREMIUM_FILE = "premium_icons.json"
PREMIUM_ICONS = {}
if os.path.exists(PREMIUM_FILE):
    try:
        with open(PREMIUM_FILE, "r", encoding="utf-8") as f:
            PREMIUM_ICONS = json.load(f)
            print(f"Da load {len(PREMIUM_ICONS)} icon premium!")
    except Exception as e:
        print(f"Loi load premium: {e}")
        PREMIUM_ICONS = {}

def pe_by_id(eid, fallback=">"):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

def pe(name, fallback=">"):
    eid = PREMIUM_ICONS.get(name)
    if eid:
        return pe_by_id(eid, fallback)
    if PREMIUM_ICONS:
        any_id = list(PREMIUM_ICONS.values())[0]
        return pe_by_id(any_id, fallback)
    return fallback

def save_premium():
    with open(PREMIUM_FILE, "w", encoding="utf-8") as f:
        json.dump(PREMIUM_ICONS, f, ensure_ascii=False, indent=2)

def auto_premium_caption(text):
    if not text:
        return text
    if not PREMIUM_ICONS:
        return text
    ids = list(PREMIUM_ICONS.values())
    if len(ids) == 0:
        return text
    if "<tg-emoji" in text:
        return text
    first_id = ids[0]
    for k in ["@", "#", ">"]:
        if k in text:
            text = text.replace(k, pe_by_id(first_id, k))
    if "<tg-emoji" not in text and len(ids) >= 1:
        text = f"{pe_by_id(first_id, '✨')} {text} {pe_by_id(first_id, '✨')}"
    return text

def caption_to_html(message):
    text = message.caption or ""
    entities = message.caption_entities or []
    if not entities:
        return auto_premium_caption(text)
    entities = sorted(entities, key=lambda e: e.offset)
    result = ""
    last = 0
    new_icons = 0
    for ent in entities:
        result += text[last:ent.offset]
        seg = text[ent.offset:ent.offset+ent.length]
        if ent.type == MessageEntity.CUSTOM_EMOJI:
            eid = ent.custom_emoji_id
            if eid not in PREMIUM_ICONS.values():
                key = "icon_" + str(len(PREMIUM_ICONS) + 1)
                PREMIUM_ICONS[key] = eid
                new_icons += 1
            result += pe_by_id(eid, seg)
        else:
            result += seg
        last = ent.offset + ent.length
    result += text[last:]
    if new_icons > 0:
        save_premium()
        print(f"Da luu them {new_icons} icon moi!")
    return result

# FIX: Cho phép tất cả user xem icon để test, không chặn ADMIN nữa
async def bat_nhieu_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    # Nếu không có entities custom emoji
    if not msg.entities:
        await msg.reply_text(f"My gui icon Premium di! Hien tai da co {len(PREMIUM_ICONS)} icon. Gui 10-20 icon 1 lan nha!")
        return
    dem = 0
    for ent in msg.entities:
        if ent.type == MessageEntity.CUSTOM_EMOJI:
            if ent.custom_emoji_id not in PREMIUM_ICONS.values():
                key = "icon_" + str(len(PREMIUM_ICONS) + 1)
                PREMIUM_ICONS[key] = ent.custom_emoji_id
                dem += 1
    if dem:
        save_premium()
        await msg.reply_text(f"Da luu {dem} icon moi! Tong {len(PREMIUM_ICONS)} icon - Gio dang bai se lap lanh!", parse_mode="HTML")
        if PREMIUM_ICONS:
            first_id = list(PREMIUM_ICONS.values())[0]
            await msg.reply_text(f"Test icon: {pe_by_id(first_id, 'TEST')} Lap lanh chua My?", parse_mode="HTML")
    else:
        await msg.reply_text(f"Da co roi! Tong {len(PREMIUM_ICONS)} icon roi My oi! Go /xemicon de xem", parse_mode="HTML")

# FIX: Bo check ADMIN_ID, ai go cung tra loi
async def xem_all_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Co nguoi go xemicon: {update.effective_user.id}")
    if not PREMIUM_ICONS:
        await update.message.reply_text("Chua co icon nao! My gui icon premium vao chat rieng voi bot di!")
        return
    lines = []
    for k, v in list(PREMIUM_ICONS.items())[:20]:
        lines.append(f"{pe_by_id(v, '>')} {k} : {v}")
    txt = f"Co {len(PREMIUM_ICONS)} icon (hien 20 dau):\n" + "\n".join(lines)
    await update.message.reply_text(txt, parse_mode="HTML")

async def test_icon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Co nguoi go testicon: {update.effective_user.id}")
    if not PREMIUM_ICONS:
        await update.message.reply_text("Chua co icon! Gui icon premium vao chat rieng truoc!")
        return
    ids = list(PREMIUM_ICONS.values())[:5]
    txt = "Test 5 icon dau:\n"
    for eid in ids:
        txt += pe_by_id(eid, "✨") + " "
    txt += "\nNeu thay 5 icon lap lanh la OK! Tong: " + str(len(PREMIUM_ICONS))
    await update.message.reply_text(txt, parse_mode="HTML")

def ensure_logo():
    if not os.path.exists(LOGO_PATH) and LOGO_B64:
        try:
            with open(LOGO_PATH, "wb") as f:
                f.write(base64.b64decode(LOGO_B64))
        except:
            pass

def get_keyboard(bot_username=None):
    if bot_username:
        link = "https://t.me/" + bot_username + "?start=thongke"
    else:
        link = PRIVATE_GROUP_LINK
    return InlineKeyboardMarkup([[InlineKeyboardButton("Vao Nhom Kin BCR", url=link)], [InlineKeyboardButton("Quay Thuong", callback_data="quay_thuong")]])

def add_logo(path):
    try:
        from PIL import Image
        if not os.path.exists(LOGO_PATH) or not os.path.exists(path):
            return
        base = Image.open(path).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")
        w, h = base.size
        logo.thumbnail((w//5, h//5))
        base.paste(logo, (w - logo.width - 10, h - logo.height - 10), logo)
        base.convert("RGB").save(path)
    except:
        pass

def get_bai(loai):
    try:
        if not os.path.exists(LICH_FILE):
            return None, None
        with open(LICH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        start = datetime.fromisoformat(data["start_date"])
        idx = (datetime.now() - start).days % 7 + 1
        folder = KENH_FOLDER if loai == "kenh" else NHOM_KIN_FOLDER
        jpg = os.path.join(folder, f"bai_{idx}.jpg")
        txt = os.path.join(folder, f"bai_{idx}.txt")
        cap = ""
        if os.path.exists(txt):
            with open(txt, "r", encoding="utf-8") as cf:
                cap = cf.read()
        else:
            cap = auto_premium_caption(f"Bai {idx} BCR VIP")
        if os.path.exists(jpg):
            return jpg, cap
        else:
            print(f"Khong tim thay file {jpg}")
            return None, cap
    except Exception as e:
        print(f"Loi get_bai: {e}")
        return None, None

async def dang_bai_20h(context):
    try:
        jpg, cap = get_bai("kenh")
        if not jpg:
            print("Khong co bai kenh de dang")
            # Thu dang file mac dinh
            if os.path.exists(IMAGE_PATH):
                with open(IMAGE_PATH, "rb") as f:
                    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=f, caption=auto_premium_caption("Test bai Kênh"), parse_mode="HTML")
                return
            return
        cap = auto_premium_caption(cap)
        with open(jpg, "rb") as f:
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=f, caption=cap, parse_mode="HTML")
        print(f"Da dang kenh: {jpg}")
    except Exception as e:
        print(f"Loi dang kenh: {e}")

async def dang_bai_nhom_kin_20h(context):
    try:
        jpg, cap = get_bai("nhom_kin")
        if not jpg:
            print("Khong co bai nhom kin de dang")
            return
        cap = auto_premium_caption(cap)
        with open(jpg, "rb") as f:
            await context.bot.send_photo(chat_id=GROUP_ID, photo=f, caption=cap, parse_mode="HTML")
        print(f"Da dang nhom kin: {jpg}")
    except Exception as e:
        print(f"Loi dang nhom kin: {e}")

async def bao_cao_cuoi_ngay(context):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Bao cao: {check_lich()}\nIcon: {len(PREMIUM_ICONS)}")
    except:
        pass

async def start_command(u, c):
    await u.message.reply_text("Bot BCR VIP dang chay! Icon: " + str(len(PREMIUM_ICONS)))

async def chao_thanh_vien_moi(u, c):
    try:
        if u.chat_member.new_chat_member.status == ChatMemberStatus.MEMBER:
            uid = u.chat_member.new_chat_member.user.id
            inv = u.chat_member.invite_link
            if inv and inv.creator:
                inviter = inv.creator.id
                invite_data[inviter] = invite_data.get(inviter, 0) + 1
            await c.bot.send_message(chat_id=u.effective_chat.id, text="Chao mung!", reply_markup=get_keyboard(c.bot.username))
    except:
        pass

async def auto_reply_tu_dong(u, c):
    if u.effective_chat.id != GROUP_ID:
        return
    if any(k in (u.message.text or "").lower() for k in ["bet", "cau", "chot", "bcr", "bai"]):
        await u.message.reply_text("Phan tich o nhom rieng roi nha!", reply_markup=get_keyboard(c.bot.username))

async def ban_command(u, c):
    if not c.args:
        await u.message.reply_text("Dung: /ban <user_id>")
        return
    try:
        uid = int(c.args[0])
        await c.bot.ban_chat_member(chat_id=GROUP_ID, user_id=uid)
        await u.message.reply_text("Da ban " + str(uid))
    except Exception as e:
        await u.message.reply_text("Loi: " + str(e))

async def top_command(u, c):
    if not invite_data:
        await u.message.reply_text("Chua co ai moi!")
        return
    top = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    await u.message.reply_text("TOP:\n" + "\n".join(["- ID " + str(uid) + ": " + str(cnt) for uid, cnt in top]))

async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        # Cho phep admin 8632660546 va nguoi go lenh xem_lich cung duoc up anh
        print(f"Nguoi la up anh: {update.effective_user.id}")
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    caption_html = caption_to_html(update.message)
    low = (update.message.caption or "").lower()
    loai = "nhom_kin" if "nhom" in low or "kin" in low else "kenh"
    folder = NHOM_KIN_FOLDER if loai == "nhom_kin" else KENH_FOLDER
    for i in range(1, 8):
        if "bai_" + str(i) in low or "bai " + str(i) in low:
            path = os.path.join(folder, "bai_" + str(i) + ".jpg")
            cap_path = os.path.join(folder, "bai_" + str(i) + ".txt")
            f = await update.message.photo[-1].get_file()
            await f.download_to_drive(path)
            add_logo(path)
            if caption_html.strip():
                with open(cap_path, "w", encoding="utf-8") as cf:
                    cf.write(caption_html.strip())
            print(f"Da luu {loai} bai_{i} caption: {caption_html[:200]}")
            await update.message.reply_text("Da luu " + loai.upper() + " bai_" + str(i) + f"\nCaption: {caption_html[:100]}", reply_markup=get_keyboard(context.bot.username), parse_mode="HTML")
            return
    f = await update.message.photo[-1].get_file()
    await f.download_to_drive(IMAGE_PATH)
    if caption_html.strip():
        with open("caption.txt", "w", encoding="utf-8") as cf:
            cf.write(caption_html.strip())
    add_logo(IMAGE_PATH)
    await update.message.reply_text(f"OK My! Da luu! Caption: {caption_html[:100]}", reply_markup=get_keyboard(context.bot.username), parse_mode="HTML")

async def test_dang_bai_command(u, c):
    print(f"Co nguoi go testdangbai: {u.effective_user.id}")
    await u.message.reply_text(f"Dang test dang bai... Icon: {len(PREMIUM_ICONS)}")
    try:
        await dang_bai_20h(c)
        await asyncio.sleep(2)
        await dang_bai_nhom_kin_20h(c)
        await u.message.reply_text("Test xong! 2 bai khac nhau! Kiem tra Kênh xem co icon lap lanh chua? Neu khong thay bai, go /xem_lich")
    except Exception as e:
        await u.message.reply_text("Loi test dang bai: " + str(e))
        print(f"Loi test: {e}")

def check_lich():
    lines = []
    for i in range(1, 8):
        k = "OK" if os.path.exists(os.path.join(KENH_FOLDER, "bai_" + str(i) + ".jpg")) else "NO"
        n = "OK" if os.path.exists(os.path.join(NHOM_KIN_FOLDER, "bai_" + str(i) + ".jpg")) else "NO"
        lines.append("Ngay " + str(i) + ": Kenh " + k + " | Nhom kin " + n)
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r") as f:
                d = json.load(f)
            lines.append("Start: " + d.get("start_date",""))
        except:
            pass
    else:
        lines.append("Chua co lich! Go /setup_lich")
    lines.append(f"Icon: {len(PREMIUM_ICONS)}")
    return "\n".join(lines)

async def setup_lich_command(u, c):
    print(f"Co nguoi go setup_lich: {u.effective_user.id}")
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    with open(LICH_FILE, "w", encoding="utf-8") as f:
        json.dump({"start_date": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    await u.message.reply_text("LICH DA SETUP:\n" + check_lich())

async def xem_lich_command(u, c):
    print(f"Co nguoi go xem_lich: {u.effective_user.id}")
    await u.message.reply_text("LICH:\n" + check_lich())

async def quay_thuong(u, c):
    q = u.callback_query
    await q.answer()
    await q.edit_message_text("Chuc mung! Vao nhom kin de nhan thuong:", reply_markup=get_keyboard(c.bot.username))

async def post_init(application):
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("Da xoa webhook cu - tranh Conflict!")
    except Exception as e:
        print(f"Khong xoa webhook: {e}")

async def error_handler(update, context):
    if isinstance(context.error, Conflict):
        print("Conflict - dang co 2 bot chay, doi 10s...")
        await asyncio.sleep(10)
        return
    print(f"Loi: {context.error}")

def main():
    ensure_logo()
    for fd in [KENH_FOLDER, NHOM_KIN_FOLDER, SCHEDULE_FOLDER]:
        os.makedirs(fd, exist_ok=True)
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("setup_lich", setup_lich_command))
    app.add_handler(CommandHandler("xem_lich", xem_lich_command))
    app.add_handler(CommandHandler("xemlich", xem_lich_command))
    app.add_handler(CommandHandler("testdangbai", test_dang_bai_command))
    app.add_handler(CommandHandler("xemicon", xem_all_icon))
    app.add_handler(CommandHandler("xem_icon", xem_all_icon))
    app.add_handler(CommandHandler("testicon", test_icon_command))
    app.add_handler(CommandHandler("test_icon", test_icon_command))
    app.add_handler(CallbackQueryHandler(quay_thuong, pattern="quay_thuong"))
    app.add_handler(ChatMemberHandler(chao_thanh_vien_moi, ChatMemberHandler.CHAT_MEMBER))
    # FIX: Bo filter ADMIN_ID de ai cung test duoc
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, bat_nhieu_icon))
    app.add_handler(MessageHandler(filters.PHOTO, nhan_anh_moi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, auto_reply_tu_dong))
    app.add_error_handler(error_handler)
    
    if app.job_queue:
        app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))
        app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))
        app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=16, minute=0, second=0))
    
    print(f"Bot BCR - FIX XEMICON - Da load {len(PREMIUM_ICONS)} icon - Dang chay!")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
