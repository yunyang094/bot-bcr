import os, json, logging, glob, asyncio, time
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import Conflict

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
FILE_ICON = "premium_icons.json"
LICH_FILE = "lich_thi_dau.json"
SCHEDULE_FOLDER = "lichthidau"

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

# --- LICH ---
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
        except Exception as e:
            logging.error(f"Loi doc {LICH_FILE}: {e}")
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
    await update.message.reply_text(f"Bot BCR gon gang dang chay!\nCo {len(icons)} icon - Go /lich de xem lich")

async def xemicon(update: Update, context):
    try:
        if not icons:
            await update.message.reply_text("Chua co icon! Gui icon premium vao group di My!")
            return
        list_ids = list(icons.values())[:5]
        text = "  " * len(list_ids)
        entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
        await update.message.reply_text(f"Test {len(icons)} icon:\n{text}", entities=entities)
    except Exception as e:
        await update.message.reply_text(f"Loi xemicon: {e}")

async def layid(update: Update, context):
    save_icons()
    if os.path.exists(FILE_ICON) and icons:
        await update.message.reply_document(open(FILE_ICON, "rb"), caption=f"Tong {len(icons)} icon")
    else:
        await update.message.reply_text("Chua co file icon!")

async def lich(update: Update, context):
    data = load_lich()
    if not data:
        await update.message.reply_text("Chua co lich! Tao file lich_thi_dau.json tren Github di My!")
        return
    msg = "Lich thi dau:\n\n"
    for i, item in enumerate(data[:20], 1):
        if isinstance(item, dict):
            msg += f"{i}. {item.get('tran','')} - {item.get('gio','')} - {item.get('kenh','')}\n"
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

async def post_init(application: Application):
    # Xoa webhook cu moi lan start - chong xung dot
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("Da xoa webhook - chong xung dot!")
    except:
        pass

def main():
    if not BOT_TOKEN:
        print("THIEU BOT_TOKEN!")
        return
    
    # VONG LAP CHONG XUNG DOT - Neu bi Conflict thi ngu 15s roi chay lai, khong crash
    while True:
        try:
            print("Dang khoi dong bot BCR gon gang...")
            app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("xemicon", xemicon))
            app.add_handler(CommandHandler("layid", layid))
            app.add_handler(CommandHandler("lay_id_icon", layid))
            app.add_handler(CommandHandler("lich", lich))
            app.add_handler(CommandHandler("lichthidau", lich))
            app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), handle_premium))
            
            print("Bot chay polling - se tu dong xu ly neu bi Conflict")
            app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, close_loop=False)
            
        except Conflict as e:
            print(f"Bi Conflict (Render dang doi ca) - Ngu 15s roi chay lai... {e}")
            time.sleep(15)
            continue
        except Exception as e:
            print(f"Loi khac: {e} - Ngu 10s roi chay lai...")
            time.sleep(10)
            continue
        break

if __name__ == "__main__":
    main()
