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

def save_premium():
    with open(PREMIUM_FILE, "w", encoding="utf-8") as f:
        json.dump(PREMIUM_ICONS, f, ensure_ascii=False, indent=2)

def auto_premium_caption(text):
    if not text or not PREMIUM_ICONS:
        return text
    ids = list(PREMIUM_ICONS.values())
    if "<tg-emoji" in text or len(ids)==0:
        return text
    first_id = ids[0]
    for k in ["@", "#", ">"]:
        if k in text:
            text = text.replace(k, pe_by_id(first_id, k))
    if "<tg-emoji" not in text:
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
    for ent in entities:
        result += text[last:ent.offset]
        seg = text[ent.offset:ent.offset+ent.length]
        if ent.type == MessageEntity.CUSTOM_EMOJI:
            eid = ent.custom_emoji_id
            if eid not in PREMIUM_ICONS.values():
                key = "icon_" + str(len(PREMIUM_ICONS) + 1)
                PREMIUM_ICONS[key] = eid
                save_premium()
            result += pe_by_id(eid, seg)
        else:
            result += seg
        last = ent.offset + ent.length
    result += text[last:]
    return result

async def bat_nhieu_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.entities:
        await msg.reply_text(f"Hien tai co {len(PREMIUM_ICONS)} icon. My gui 10 icon Premium 1 lan di!")
        return
    dem = 0
    for ent in msg.entities:
        if ent.type == MessageEntity.CUSTOM_EMOJI:
            if ent.custom_emoji_id not in PREMIUM_ICONS.values():
                key = f"icon_{len(PREMIUM_ICONS)+1}"
                PREMIUM_ICONS[key] = ent.custom_emoji_id
                dem += 1
    if dem:
        save_premium()
        await msg.reply_text(f"Da luu {dem} icon moi! Tong {len(PREMIUM_ICONS)}!", parse_mode="HTML")
    else:
        await msg.reply_text(f"Da co roi! Tong {len(PREMIUM_ICONS)} icon! Go /xemicon", parse_mode="HTML")

async def xem_all_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # BO CHAN ADMIN - AI GO CUNG DUOC
    print(f"Xemicon tu {update.effective_user.id}")
    if not PREMIUM_ICONS:
        await update.message.reply_text("Chua co icon nao!")
        return
    lines = []
    for k, v in list(PREMIUM_ICONS.items())[:20]:
        lines.append(f"{pe_by_id(v, '>')} {k}: {v}")
    txt = f"Co {len(PREMIUM_ICONS)} icon (hien 20 dau):\n" + "\n".join(lines)
    await update.message.reply_text(txt, parse_mode="HTML")

async def test_icon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PREMIUM_ICONS:
        await update.message.reply_text("Chua co icon!")
        return
    ids = list(PREMIUM_ICONS.values())[:5]
    txt = "Test 5 icon:\n"
    for eid in ids:
        txt += pe_by_id(eid, "✨") + " "
    txt += f"\nTong: {len(PREMIUM_ICONS)}"
    await update.message.reply_text(txt, parse_mode="HTML")

async def lay_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(PREMIUM_FILE):
        await update.message.reply_text("Chua co file json!")
        return
    with open(PREMIUM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    await update.message.reply_document(document=open(PREMIUM_FILE, "rb"), filename=f"premium_icons_{len(data)}.json", caption=f"Tong {len(data)} icon")
    with open("all_ids.txt","w",encoding="utf-8") as out:
        for k,v in data.items():
            out.write(f"{k}: {v}\n")
    await update.message.reply_document(document=open("all_ids.txt","rb"), filename="all_ids.txt")

async def my_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"ID cua My la: {uid}\nChat ID: {chat_id}\nAdmin ID trong code: {ADMIN_ID}\nIcon: {len(PREMIUM_ICONS)}\nMy dang chat o: {update.effective_chat.type}")

def ensure_logo():
    pass

def get_keyboard(bot_username=None):
    link = "https://t.me/" + bot_username + "?start=thongke" if bot_username else PRIVATE_GROUP_LINK
    return InlineKeyboardMarkup([[InlineKeyboardButton("Vao Nhom Kin BCR", url=link)]])

def add_logo(path):
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
        return None, cap
    except Exception as e:
        print(f"Loi get_bai: {e}")
        return None, None

async def dang_bai_20h(context):
    try:
        jpg, cap = get_bai("kenh")
        if not jpg:
            if os.path.exists(IMAGE_PATH):
                with open(IMAGE_PATH, "rb") as f:
                    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=f, caption=auto_premium_caption("Test Kênh"), parse_mode="HTML")
            return
        cap = auto_premium_caption(cap)
        with open(jpg, "rb") as f:
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=f, caption=cap, parse_mode="HTML")
    except Exception as e:
        print(f"Loi dang kenh: {e}")

async def dang_bai_nhom_kin_20h(context):
    try:
        jpg, cap = get_bai("nhom_kin")
        if not jpg:
            return
        cap = auto_premium_caption(cap)
        with open(jpg, "rb") as f:
            await context.bot.send_photo(chat_id=GROUP_ID, photo=f, caption=cap, parse_mode="HTML")
    except Exception as e:
        print(f"Loi dang nhom kin: {e}")

async def bao_cao_cuoi_ngay(context):
    pass

async def start_command(u, c):
    await u.message.reply_text(f"Bot chay! ID My: {u.effective_user.id} | Icon: {len(PREMIUM_ICONS)}\nLenh: /xemicon /testicon /layid /myid /xem_lich /testdangbai")

async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            if caption_html.strip():
                with open(cap_path, "w", encoding="utf-8") as cf:
                    cf.write(caption_html.strip())
            await update.message.reply_text("Da luu " + loai.upper() + " bai_" + str(i), reply_markup=get_keyboard(context.bot.username), parse_mode="HTML")
            return
    f = await update.message.photo[-1].get_file()
    await f.download_to_drive(IMAGE_PATH)
    if caption_html.strip():
        with open("caption.txt", "w", encoding="utf-8") as cf:
            cf.write(caption_html.strip())
    await update.message.reply_text(f"OK My! Da luu!", reply_markup=get_keyboard(context.bot.username), parse_mode="HTML")

async def test_dang_bai_command(u, c):
    await u.message.reply_text(f"Dang test... Icon: {len(PREMIUM_ICONS)}")
    try:
        await dang_bai_20h(c)
        await asyncio.sleep(2)
        await dang_bai_nhom_kin_20h(c)
        await u.message.reply_text("Test xong! Kiem tra Kênh")
    except Exception as e:
        await u.message.reply_text("Loi: " + str(e))

def check_lich():
    lines = []
    for i in range(1, 8):
        k = "OK" if os.path.exists(os.path.join(KENH_FOLDER, "bai_" + str(i) + ".jpg")) else "NO"
        n = "OK" if os.path.exists(os.path.join(NHOM_KIN_FOLDER, "bai_" + str(i) + ".jpg")) else "NO"
        lines.append(f"Ngay {i}: Kenh {k} | Nhom kin {n}")
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
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    with open(LICH_FILE, "w", encoding="utf-8") as f:
        json.dump({"start_date": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    await u.message.reply_text("LICH DA SETUP:\n" + check_lich())

async def xem_lich_command(u, c):
    await u.message.reply_text("LICH:\n" + check_lich())

async def post_init(application):
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

async def error_handler(update, context):
    print(f"Loi: {context.error}")

def main():
    for fd in [KENH_FOLDER, NHOM_KIN_FOLDER, SCHEDULE_FOLDER]:
        os.makedirs(fd, exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("myid", my_id_command))
    app.add_handler(CommandHandler("my_id", my_id_command))
    app.add_handler(CommandHandler("setup_lich", setup_lich_command))
    app.add_handler(CommandHandler("xem_lich", xem_lich_command))
    app.add_handler(CommandHandler("xemlich", xem_lich_command))
    app.add_handler(CommandHandler("testdangbai", test_dang_bai_command))
    app.add_handler(CommandHandler("xemicon", xem_all_icon))
    app.add_handler(CommandHandler("xem_icon", xem_all_icon))
    app.add_handler(CommandHandler("testicon", test_icon_command))
    app.add_handler(CommandHandler("test_icon", test_icon_command))
    app.add_handler(CommandHandler("layid", lay_id_command))
    app.add_handler(CommandHandler("lay_id", lay_id_command))
    app.add_handler(CommandHandler("exporticon", lay_id_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, bat_nhieu_icon))
    app.add_handler(MessageHandler(filters.PHOTO, nhan_anh_moi))
    app.add_error_handler(error_handler)
    if app.job_queue:
        app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))
        app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))
    print(f"Bot FIX ADMIN - {len(PREMIUM_ICONS)} icon")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
