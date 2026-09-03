import os, json, logging, glob
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters

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
    # 1. Doc file lich_thi_dau.json goc
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
    # 2. Doc tat ca file json trong thu muc lichthidau/
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
    await update.message.reply_text(f"✅ Bot BCR dang chay!\n💎 {len(icons)} icon\n📅 /lich de xem lich\n💾 /layid de lay file icon")

async def xemicon(update: Update, context):
    try:
        if not icons:
            await update.message.reply_text("⚠️ Chua co icon! Gui icon premium vao group de bot hoc!")
            return
        list_ids = list(icons.values())[:5]
        text = "  " * len(list_ids)
        entities = [MessageEntity(type=MessageEntity.CUSTOM_EMOJI, offset=i*2, length=2, custom_emoji_id=str(cid)) for i, cid in enumerate(list_ids)]
        await update.message.reply_text(f"Test {len(icons)} icon:\n{text}", entities=entities)
    except Exception as e:
        await update.message.reply_text(f"Loi: {e}")

async def layid(update: Update, context):
    save_icons()
    if os.path.exists(FILE_ICON) and icons:
        await update.message.reply_document(open(FILE_ICON, "rb"), caption=f"Tong {len(icons)} icon")
    else:
        await update.message.reply_text("Chua co file icon, gui icon premium vao group truoc nha!")

async def lich(update: Update, context):
    data = load_lich()
    if not data:
        msg = "📅 CHƯA CÓ LỊCH THI ĐẤU\n\n"
        msg += "My làm vầy để setup:\n"
        msg += "1. Vô Github repo yunyang094/bot-bcr\n"
        msg += "2. Tạo file tên `lich_thi_dau.json` ở thư mục gốc\n"
        msg += "3. Dán nội dung theo mẫu:\n"
        msg += '[\n  {"giai":"Ngoai Hang Anh","gio":"22:00 - 03/09","kenh":"K+PM","tran":"Man City vs Arsenal"}\n]\n\n'
        msg += f"Debug: Tim thay file {LICH_FILE}={os.path.exists(LICH_FILE)}, folder {SCHEDULE_FOLDER}={os.path.exists(SCHEDULE_FOLDER)}"
        await update.message.reply_text(msg)
        return
    
    msg = "📅 LỊCH THI ĐẤU HÔM NAY\n\n"
    for i, item in enumerate(data[:30], 1):
        if isinstance(item, dict):
            giai = item.get('giai','')
            gio = item.get('gio','')
            tran = item.get('tran', item.get('doi',''))
            kenh = item.get('kenh','')
            msg += f"{i}. [{giai}] {tran}\n   ⏰ {gio} | 📺 {kenh}\n\n"
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
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("Bot BCR full lich + icon - started")

def main():
    if not BOT_TOKEN:
        print("THIEU BOT_TOKEN!")
        return
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xemicon", xemicon))
    app.add_handler(CommandHandler("layid", layid))
    app.add_handler(CommandHandler("lay_id_icon", layid))
    app.add_handler(CommandHandler("lich", lich))
    app.add_handler(CommandHandler("lichthidau", lich))
    app.add_handler(MessageHandler(filters.Entity(MessageEntity.CUSTOM_EMOJI), handle_premium))
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
