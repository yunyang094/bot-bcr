import os, json, base64, logging
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ChatMemberHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatMemberStatus
import asyncio

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
    except:
        PREMIUM_ICONS = {}

def pe(name, fallback=">"):
    eid = PREMIUM_ICONS.get(name)
    if eid:
        return '<tg-emoji emoji-id="' + eid + '">' + fallback + '</tg-emoji>'
    return fallback

def save_premium():
    with open(PREMIUM_FILE, "w", encoding="utf-8") as f:
        json.dump(PREMIUM_ICONS, f, ensure_ascii=False, indent=2)

EMOJI_MAP = {"@": "check", "#": "tangtruong"}

def auto_premium_caption(text):
    if not text:
        return text
    for k, v in EMOJI_MAP.items():
        if v in PREMIUM_ICONS:
            text = text.replace(k, pe(v, k))
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
            result += '<tg-emoji emoji-id="' + eid + '">' + seg + '</tg-emoji>'
        else:
            result += seg
        last = ent.offset + ent.length
    result += text[last:]
    return auto_premium_caption(result)

async def bat_nhieu_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.entities:
        await msg.reply_text("My gui icon Premium di!")
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
        await msg.reply_text("Da luu " + str(dem) + " icon! Tong " + str(len(PREMIUM_ICONS)))
    else:
        await msg.reply_text("Da co roi! Tong " + str(len(PREMIUM_ICONS)))

async def xem_all_icon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not PREMIUM_ICONS:
        await update.message.reply_text("Chua co icon nao!")
        return
    lines = []
    for k, v in list(PREMIUM_ICONS.items())[:20]:
        lines.append(pe(k, ">") + " " + k + " : " + v)
    txt = "Co " + str(len(PREMIUM_ICONS)) + " icon:\n" + "\n".join(lines)
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
        link = "https://t.me/doccaubcr_bot?start=thongke"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("VAO NHOM KIN VIP", url=PRIVATE_GROUP_LINK)],
        [InlineKeyboardButton("LIEN HE AD", url=LINK_LIEN_HE_AD), InlineKeyboardButton("XEM THONG KE", url=link)],
        [InlineKeyboardButton("QUAY THUONG", callback_data="quay_thuong")]
    ])

def add_logo(image_path):
    ensure_logo()
    try:
        from PIL import Image, ImageDraw
        if not os.path.exists(image_path) or not os.path.exists(LOGO_PATH):
            return
        board = Image.open(image_path).convert("RGBA")
        W, H = board.size
        logo = Image.open(LOGO_PATH).convert("RGBA")
        s1 = int(W * 0.18)
        l1 = logo.resize((s1, s1), Image.LANCZOS)
        bg = Image.new("RGBA", (int(s1 * 1.15), int(s1 * 1.15)), (0, 0, 0, 0))
        ImageDraw.Draw(bg).ellipse([0, 0, bg.size[0]-1, bg.size[1]-1], fill=(255, 255, 255, 230), outline=(0, 0, 0, 200), width=2)
        x = W - bg.size[0] - int(H * 0.04)
        y = H - bg.size[1] - int(H * 0.04)
        board.alpha_composite(bg, (x, y))
        board.alpha_composite(l1, (x + (bg.size[0]-s1)//2, y + (bg.size[1]-s1)//2))
        s2 = int(W * 0.38)
        l2 = logo.resize((s2, s2), Image.LANCZOS)
        l2.putalpha(l2.split()[3].point(lambda p: int(p * 0.32)))
        board.alpha_composite(l2, ((W-s2)//2, (H-s2)//2))
        board.convert("RGB").save(image_path, "JPEG", quality=92)
    except Exception as e:
        print("Loi logo")
        print(e)

def get_bai(loai):
    folder = NHOM_KIN_FOLDER if loai == "nhom_kin" else KENH_FOLDER
    os.makedirs(folder, exist_ok=True)
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    idx = None
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r", encoding="utf-8") as f:
                lich = json.load(f)
                start_date = datetime.fromisoformat(lich.get("start_date"))
                idx = (datetime.now() - start_date).days % 7 + 1
        except:
            pass
    if idx is None:
        idx = datetime.now().weekday() + 1
    for base in [folder, SCHEDULE_FOLDER]:
        img = os.path.join(base, "bai_" + str(idx) + ".jpg")
        cap = os.path.join(base, "bai_" + str(idx) + ".txt")
        if os.path.exists(img):
            return img, cap
    if loai == "nhom_kin":
        return os.path.join(folder, "bai_1.jpg"), os.path.join(folder, "bai_1.txt")
    return IMAGE_PATH, "caption.txt"

async def dang_bai_20h(context):
    img, cap_path = get_bai("kenh")
    cap = None
    if os.path.exists(cap_path):
        with open(cap_path, "r", encoding="utf-8") as f:
            cap = f.read()
    elif os.path.exists("caption.txt"):
        with open("caption.txt", "r", encoding="utf-8") as f:
            cap = f.read()
    if not cap:
        cap = "BAI KENH " + datetime.now().strftime("%d/%m")
    cap = auto_premium_caption(cap)
    try:
        if os.path.exists(img):
            add_logo(img)
            with open(img, "rb") as ph:
                m = await context.bot.send_photo(chat_id=CHANNEL_ID, photo=ph, caption=cap, reply_markup=get_keyboard(context.bot.username), parse_mode="HTML")
            try:
                await context.bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=m.message_id, disable_notification=True)
            except:
                pass
        else:
            m = await context.bot.send_message(chat_id=CHANNEL_ID, text=cap, reply_markup=get_keyboard(context.bot.username), parse_mode="HTML")
            try:
                await context.bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=m.message_id, disable_notification=True)
            except:
                pass
        print("KENH OK " + img)
    except Exception as e:
        print("Loi kenh")
        print(e)

async def dang_bai_nhom_kin_20h(context):
    img, cap_path = get_bai("nhom_kin")
    cap = None
    if os.path.exists(cap_path):
        with open(cap_path, "r", encoding="utf-8") as f:
            cap = f.read()
    if not cap:
        cap = "CAU VIP NHOM KIN " + datetime.now().strftime("%d/%m")
    cap = auto_premium_caption(cap)
    try:
        if os.path.exists(img):
            add_logo(img)
            with open(img, "rb") as ph:
                await context.bot.send_photo(chat_id=GROUP_ID, photo=ph, caption=cap, parse_mode="HTML")
        else:
            await context.bot.send_message(chat_id=GROUP_ID, text=cap, parse_mode="HTML")
        print("NHOM KIN OK " + img)
    except Exception as e:
        print("Loi nhom kin")
        print(e)

async def bao_cao_cuoi_ngay(c):
    if not invite_data:
        return
    top = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:5]
    txt = "BAO CAO:\n" + "\n".join(["- ID " + str(uid) + ": " + str(cnt) for uid, cnt in top])
    try:
        await c.bot.send_message(chat_id=ADMIN_ID, text=txt)
    except:
        pass

async def start_command(u, c):
    uid = u.effective_user.id
    if c.args and c.args[0] == "thongke":
        if uid != ADMIN_ID:
            await u.message.reply_text("Ban khong co quyen!")
            return
        if not invite_data:
            await u.message.reply_text("Chua co ai moi!")
            return
        top = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
        await u.message.reply_text("THONG KE:\n" + "\n".join(["- ID " + str(i) + ": " + str(cc) for i, cc in top]))
        return
    if c.args:
        try:
            inv = int(c.args[0])
            if inv != uid:
                invite_data[inv] = invite_data.get(inv, 0) + 1
        except:
            pass
    await u.message.reply_text("Chao mung " + u.effective_user.first_name + "!", reply_markup=get_keyboard(c.bot.username))

async def chao_thanh_vien_moi(u, c):
    try:
        if u.chat_member.chat.id != GROUP_ID:
            return
        old = u.chat_member.old_chat_member.status
        new = u.chat_member.new_chat_member.status
        if old in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            await c.bot.send_message(chat_id=GROUP_ID, text="Chao mung " + u.chat_member.new_chat_member.user.first_name + "!", reply_markup=get_keyboard(c.bot.username))
    except:
        pass

async def auto_reply_tu_dong(u, c):
    if u.effective_chat.id != GROUP_ID:
        return
    if any(k in (u.message.text or "").lower() for k in ["bet", "cau", "chot", "bcr", "bai"]):
        await u.message.reply_text("Phan tich o nhom rieng roi nha!", reply_markup=get_keyboard(c.bot.username))

async def ban_command(u, c):
    if u.effective_user.id != ADMIN_ID:
        return
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
        return
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
            await update.message.reply_text("Da luu " + loai.upper() + " bai_" + str(i), reply_markup=get_keyboard(context.bot.username))
            return
    f = await update.message.photo[-1].get_file()
    await f.download_to_drive(IMAGE_PATH)
    if caption_html.strip():
        with open("caption.txt", "w", encoding="utf-8") as cf:
            cf.write(caption_html.strip())
    add_logo(IMAGE_PATH)
    await update.message.reply_text("OK My! Da luu!", reply_markup=get_keyboard(context.bot.username))

async def test_dang_bai_command(u, c):
    if u.effective_user.id != ADMIN_ID:
        return
    await u.message.reply_text("Dang test...")
    try:
        await dang_bai_20h(c)
        await asyncio.sleep(2)
        await dang_bai_nhom_kin_20h(c)
        await u.message.reply_text("Test xong! 2 bai khac nhau!")
    except Exception as e:
        await u.message.reply_text("Loi: " + str(e))

def check_lich():
    lines = []
    for i in range(1, 8):
        k = "OK" if os.path.exists(os.path.join(KENH_FOLDER, "bai_" + str(i) + ".jpg")) else "NO"
        n = "OK" if os.path.exists(os.path.join(NHOM_KIN_FOLDER, "bai_" + str(i) + ".jpg")) else "NO"
        lines.append("Ngay " + str(i) + ": Kenh " + k + " | Nhom kin " + n)
    return "\n".join(lines)

async def setup_lich_command(u, c):
    if u.effective_user.id != ADMIN_ID:
        return
    os.makedirs(KENH_FOLDER, exist_ok=True)
    os.makedirs(NHOM_KIN_FOLDER, exist_ok=True)
    with open(LICH_FILE, "w", encoding="utf-8") as f:
        json.dump({"start_date": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    await u.message.reply_text("LICH:\n" + check_lich())

async def xem_lich_command(u, c):
    if u.effective_user.id != ADMIN_ID:
        return
    await u.message.reply_text("LICH:\n" + check_lich())

async def quay_thuong(u, c):
    q = u.callback_query
    await q.answer()
    await q.edit_message_text("Chuc mung! Vao nhom kin de nhan thuong:", reply_markup=get_keyboard(c.bot.username))

def main():
    ensure_logo()
    for fd in [KENH_FOLDER, NHOM_KIN_FOLDER, SCHEDULE_FOLDER]:
        os.makedirs(fd, exist_ok=True)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("setup_lich", setup_lich_command))
    app.add_handler(CommandHandler("xem_lich", xem_lich_command))
    app.add_handler(CommandHandler("testdangbai", test_dang_bai_command))
    app.add_handler(CommandHandler("xemicon", xem_all_icon))
    app.add_handler(CallbackQueryHandler(quay_thuong, pattern="quay_thuong"))
    app.add_handler(ChatMemberHandler(chao_thanh_vien_moi, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.User(user_id=ADMIN_ID), bat_nhieu_icon))
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(user_id=ADMIN_ID), nhan_anh_moi))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, auto_reply_tu_dong))
    if app.job_queue:
        app.job_queue.run_daily(dang_bai_20h, time=time(hour=13, minute=0, second=0))
        app.job_queue.run_daily(dang_bai_nhom_kin_20h, time=time(hour=13, minute=5, second=0))
        app.job_queue.run_daily(bao_cao_cuoi_ngay, time=time(hour=16, minute=0, second=0))
    print("Bot BCR - FIX LOI - Dang chay!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

