import os, json, logging, glob
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
FILE_ICON = "premium_icons.json"
LICH_FILE = "lich_thi_dau.json"
SCHEDULE_FOLDER = "lichthidau"
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or ""

logging.basicConfig(level=logging.INFO)

# --- ICON ---
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

def load_lich():
    all_match = []
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_match.extend(data)
                else:
                    all_match.append(data)
        except:
            pass
    if os.path.exists(SCHEDULE_FOLDER):
        for jf in glob.glob(os.path.join(SCHEDULE_FOLDER, "*.json")):
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_match.extend(data)
                    else:
                        all_match.append(data)
            except:
                pass
    return all_match

async def start(update: Update, context):
    await update.message.reply_text(f"Bot BCR WEBHOOK dang chay! Gon gang - {len(icons)} icon")

async def xemicon(update: Update, context):
    if not icons:
        await update.message.reply_text("Chua co icon!")
        return
    list_ids = list(icons.values())[:5]
    text = "  " * len(list_ids)
    entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
    await update.message.reply_text(f"Test {len(icons)} icon:\n{text}", entities=entities)

async def layid(update: Update, context):
    save_icons()
    if os.path.exists(FILE_ICON) and icons:
        await update.message.reply_document(open(FILE_ICON, "rb"), caption=f"Tong {len(icons)} icon")
    else:
        await update.message.reply_text("Chua co file!")

async def lich(update: Update, context):
    data = load_lich()
    if not data:
        await update.message.reply_text("Chua co lich!")
        return
    msg = "Lich thi dau:\n\n"
    for i, item in enumerate(data[:20], 1):
        if isinstance(item, dict):
            msg += f"{i}. {item.get('tran','')} - {item.get('gio','')}\n"
        else:
            msg += f"{i}. {item}\n"
    await update.message.reply_text(msg[:4000])

async def handle_premium(update: Update, context):
    if not update.message or not update.message.entities:
        return
    new_count = 0
    for e in update.message.entities:
        if e.type == MessageEntity.CUSTOM_EMOJI:
            cid = str(e.custom_emoji_id)
            if cid not in reverse_icons:
                new_key = f"icon_{len(icons)+1}"
                icons[new_key] = cid
                reverse_icons[cid] = new_key
                new_count += 1
    if new_count > 0:
        save_icons()

def main():
    if not BOT_TOKEN:
        print("THIEU BOT_TOKEN!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xemicon", xemicon))
    app.add_handler(CommandHandler("layid", layid))
    app.add_handler(CommandHandler("lay_id_icon", layid))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("lichthidau", lich))
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), handle_premium))

    # NEU CO WEBHOOK_URL THI CHAY WEBHOOK - HET XUNG DOT 100%
    if WEBHOOK_URL:
        print(f"Chay WEBHOOK mode tai {WEBHOOK_URL}")
        # Render se tu cung cap RENDER_EXTERNAL_URL
        webhook_path = "/webhook"
        full_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"
        print(f"Webhook URL: {full_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path.strip("/"),
            webhook_url=full_url,
            drop_pending_updates=True
        )
    else:
        print("Khong co WEBHOOK_URL - chay polling tam thoi (se bi conflict neu co 2 instance)")
        app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
