
import os, json, random, logging
from datetime import datetime, time, timedelta
from collections import defaultdict, deque
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatMemberStatus

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/yourgroup")
ADMIN_LINK = os.getenv("ADMIN_LINK", "https://t.me/youradmin")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

logging.basicConfig(level=logging.INFO)

# ===== DATA GỌN TRONG 1 FILE - LƯU TRONG data.json =====
FILE_DATA = "data.json"

def load_data():
    if os.path.exists(FILE_DATA):
        try:
            with open(FILE_DATA,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "stats":{"total_messages":0,"users":{},"joins":0},
        "lich":{"index":0,"last_date":""},
        "tailieu":["","","","","","",""],  # 7 ngày, My gửi cho bot nó sẽ lưu vào đây
        "tailieu_file_id":[None]*7,
        "tailieu_type":["text"]*7
    }

def save_data():
    with open(FILE_DATA,"w",encoding="utf-8") as f:
        json.dump(DATA, f, indent=2, ensure_ascii=False)

DATA = load_data()

def is_admin(update: Update):
    if not update.effective_user: return False
    if update.effective_user.id in ADMIN_IDS: return True
    if update.effective_chat and update.effective_chat.type in ["group","supergroup"]:
        try:
            m = update.effective_chat.get_member(update.effective_user.id)
            return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        except:
            return False
    return False

def is_clone(u):
    if u.is_bot: return True
    if not u.username:
        name = (u.first_name or "") + (u.last_name or "")
        if len(name)<3 or name.isdigit(): return True
        if "user" in name.lower() and any(c.isdigit() for c in name): return True
    return False

user_msgs = defaultdict(lambda: deque(maxlen=10))
warnings = defaultdict(int)

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Nhóm", url=GROUP_LINK), InlineKeyboardButton("👮 Admin", url=ADMIN_LINK)],
        [InlineKeyboardButton("🎁 Quay Thưởng", callback_data="qt"), InlineKeyboardButton("📊 Thống Kê", callback_data="tk")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BOT BCR đang chạy!\n\n"
        "✅ Chào người mới\n✅ Chống spam\n✅ Kick clone\n"
        "✅ Thống kê - Quay thưởng\n✅ Đăng 20:00 kênh 7 ngày\n\n"
        "My gửi tài liệu trực tiếp cho bot ở chat riêng này, bot sẽ lưu và đăng 20:00!",
        reply_markup=main_kb()
    )

async def thongke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = DATA["stats"]
    top = sorted(s["users"].items(), key=lambda x: x[1].get("messages",0), reverse=True)[:5]
    top_t = "\n".join([f"{i+1}. {v.get('name')} - {v.get('messages')} tin" for i,(k,v) in enumerate(top)]) or "Chưa có"
    idx = DATA["lich"]["index"]
    await update.message.reply_text(
        f"📊 THỐNG KÊ\n👥 Tương tác: {len(s['users'])}\n💬 Tin nhắn: {s['total_messages']}\n👋 Vào nhóm: {s.get('joins',0)}\n"
        f"📅 Đã đăng: {idx}/7\n\n🔥 Top:\n{top_t}",
        reply_markup=main_kb()
    )

async def quaythuong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = list(DATA["stats"]["users"].values())
    if not users:
        await update.message.reply_text("Chưa có ai!")
        return
    w = random.choice(users)
    await update.message.reply_text(f"🎉 Chúc mừng {w.get('name')} trúng thưởng!\nID: {w.get('id')}", reply_markup=main_kb())

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    if not update.message.reply_to_message: 
        await update.message.reply_text("Reply người cần kick rồi /kick")
        return
    u = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, u.id)
        await context.bot.unban_chat_member(update.effective_chat.id, u.id)
        await update.message.reply_text(f"Đã kick {u.first_name}")
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for m in update.message.new_chat_members:
        DATA["stats"]["joins"]+=1
        save_data()
        if is_clone(m):
            try:
                await context.bot.ban_chat_member(update.effective_chat.id, m.id)
                await context.bot.unban_chat_member(update.effective_chat.id, m.id)
                await update.message.reply_text(f"🚫 Kick clone: {m.first_name}")
                continue
            except: pass
        await update.message.reply_html(f"👋 Chào {m.mention_html()} vào nhóm!", reply_markup=main_kb())

async def antispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    
    # Nếu là chat riêng với admin và gửi tài liệu -> lưu vào 7 ngày
    if update.effective_chat.type == "private" and is_admin(update):
        # Không phải lệnh
        if update.message.text and update.message.text.startswith("/"):
            pass
        else:
            # Lưu tài liệu My gửi
            txt = update.message.text or update.message.caption or ""
            f_id = None
            f_type = "text"
            if update.message.photo:
                f_id = update.message.photo[-1].file_id
                f_type = "photo"
            elif update.message.document:
                f_id = update.message.document.file_id
                f_type = "document"
            elif update.message.video:
                f_id = update.message.video.file_id
                f_type = "video"
            
            # Hỏi lưu vào ngày mấy
            context.user_data["pending_text"] = txt
            context.user_data["pending_file_id"] = f_id
            context.user_data["pending_type"] = f_type
            
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"Ngày {i+1}", callback_data=f"setday_{i}") for i in range(7)]])
            await update.message.reply_text(
                f"📄 My vừa gửi tài liệu:\n{txt[:200]}\n\nMy muốn lưu vào ngày mấy? (1-7)",
                reply_markup=kb
            )
            return

    # Stats cho group
    uid = str(update.effective_user.id)
    if uid not in DATA["stats"]["users"]:
        DATA["stats"]["users"][uid] = {"id":update.effective_user.id,"name":update.effective_user.first_name,"messages":0}
    DATA["stats"]["users"][uid]["messages"]+=1
    DATA["stats"]["total_messages"]+=1
    save_data()

    if is_admin(update): return
    now = datetime.now()
    user_msgs[update.effective_user.id].append(now)
    recent = [t for t in user_msgs[update.effective_user.id] if (now-t).total_seconds()<10]
    if len(recent)>=6:
        try:
            await update.message.delete()
            await context.bot.restrict_chat_member(update.effective_chat.id, update.effective_user.id, until_date=now+timedelta(minutes=5))
            await context.bot.send_message(update.effective_chat.id, f"⚠️ {update.effective_user.mention_html()} spam! Mute 5p", parse_mode="HTML")
            user_msgs[update.effective_user.id].clear()
            return
        except: pass

    text = (update.message.text or update.message.caption or "").lower()
    if text.count("http")>=2 or "@all" in text or "@everyone" in text:
        try:
            await update.message.delete()
            warnings[update.effective_user.id]+=1
            if warnings[update.effective_user.id]>=3:
                await context.bot.restrict_chat_member(update.effective_chat.id, update.effective_user.id, until_date=now+timedelta(minutes=30))
                await context.bot.send_message(update.effective_chat.id, f"🚫 {update.effective_user.first_name} spam link! Mute 30p")
                warnings[update.effective_user.id]=0
            else:
                await context.bot.send_message(update.effective_chat.id, f"⚠️ Cấm spam link! {warnings[update.effective_user.id]}/3")
            return
        except: pass

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    
    if data.startswith("setday_"):
        idx = int(data.split("_")[1])
        txt = context.user_data.get("pending_text","")
        fid = context.user_data.get("pending_file_id")
        ftype = context.user_data.get("pending_type","text")
        
        DATA["tailieu"][idx] = txt
        DATA["tailieu_file_id"][idx] = fid
        DATA["tailieu_type"][idx] = ftype
        save_data()
        
        await q.edit_message_text(f"✅ Đã lưu vào NGÀY {idx+1}:\n{txt[:300]}\n\n20:00 sẽ đăng ngày này lên kênh!")
    
    elif data=="tk":
        s = DATA["stats"]
        await q.message.reply_text(f"📊 Tổng: {s['total_messages']} tin - {len(s['users'])} người - Đã đăng {DATA['lich']['index']}/7", reply_markup=main_kb())
    elif data=="qt":
        users = list(DATA["stats"]["users"].values())
        if users:
            w = random.choice(users)
            await q.message.reply_text(f"🎉 Chúc mừng {w.get('name')} trúng thưởng!", reply_markup=main_kb())

async def setbai_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update) or update.effective_chat.type!="private":
        await update.message.reply_text("Chỉ admin chat riêng mới set được! Gửi tài liệu trực tiếp cho bot là được My!")
        return
    # /setbai 1 nội dung
    if len(context.args)<2:
        await update.message.reply_text("Dùng: /setbai <1-7> <nội dung>\nHoặc gửi ảnh/tài liệu trực tiếp cho bot!")
        return
    try:
        idx = int(context.args[0])-1
        if 0<=idx<7:
            content = " ".join(context.args[1:])
            DATA["tailieu"][idx]=content
            save_data()
            await update.message.reply_text(f"✅ Đã set ngày {idx+1}: {content[:200]}")
    except:
        await update.message.reply_text("Lỗi! /setbai 1 Nội dung ngày 1")

async def xemtailieu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    msg = "📚 TÀI LIỆU 7 NGÀY ĐÃ LƯU:\n\n"
    for i in range(7):
        t = DATA["tailieu"][i]
        fid = DATA["tailieu_file_id"][i]
        status = "✅ Có" if (t or fid) else "❌ Trống"
        preview = (t[:30]+"...") if t else ("Có file" if fid else "Trống")
        msg+=f"Ngày {i+1}: {status} - {preview}\n"
    msg+="\nMy gửi tài liệu (text/ảnh/file) trực tiếp cho bot ở chat riêng này để set nhé!"
    await update.message.reply_text(msg)

async def job_20h(context: ContextTypes.DEFAULT_TYPE):
    if not CHANNEL_ID:
        logging.warning("Chưa có CHANNEL_ID")
        return
    idx = DATA["lich"]["index"]
    if idx>=7: idx=0
    
    txt = DATA["tailieu"][idx]
    fid = DATA["tailieu_file_id"][idx]
    ftype = DATA["tailieu_type"][idx]
    
    if not txt and not fid:
        # Nếu ngày này chưa có tài liệu, bỏ qua
        logging.info(f"Ngày {idx+1} chưa có tài liệu, bỏ qua")
        DATA["lich"]["index"] = (idx+1)%7
        save_data()
        return
    
    try:
        kb = main_kb()
        caption = txt or f"📚 Tài liệu ngày {idx+1}"
        if fid:
            if ftype=="photo":
                await context.bot.send_photo(CHANNEL_ID, photo=fid, caption=caption, reply_markup=kb, parse_mode="HTML")
            elif ftype=="document":
                await context.bot.send_document(CHANNEL_ID, document=fid, caption=caption, reply_markup=kb, parse_mode="HTML")
            elif ftype=="video":
                await context.bot.send_video(CHANNEL_ID, video=fid, caption=caption, reply_markup=kb, parse_mode="HTML")
        else:
            await context.bot.send_message(CHANNEL_ID, text=caption, reply_markup=kb, parse_mode="HTML")
        
        DATA["lich"]["index"] = (idx+1)%7
        DATA["lich"]["last_date"]=datetime.now().isoformat()
        save_data()
        logging.info(f"Đã đăng ngày {idx+1}")
    except Exception as e:
        logging.error(f"Lỗi đăng: {e}")

def main():
    import asyncio
    # Fix cho Python 3.12+ / 3.14 trên Render - tạo event loop nếu chưa có
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if not os.getenv("BOT_TOKEN"):
        print("THIEU BOT_TOKEN!")
        return
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("thongke", thongke))
    app.add_handler(CommandHandler("quaythuong", quaythuong))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("setbai", setbai_cmd))
    app.add_handler(CommandHandler("xemtailieu", xemtailieu))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.NEW_CHAT_MEMBERS, antispam))
    # 20:00 VN = 13:00 UTC
    app.job_queue.run_daily(job_20h, time=time(hour=13, minute=0), name="20h")
    print("BOT GON 1 FILE DANG CHAY - My gui tai lieu truc tiep cho bot nhe!")
    app.run_polling(drop_pending_updates=True, allowed_updates=None)

if __name__=="__main__":
    main()
