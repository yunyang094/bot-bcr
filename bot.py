import logging
import os
from datetime import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler
from telegram.constants import ChatMemberStatus

# Lấy Token từ Environment (My đã dán ở trang Environment)
# Nếu không có thì dùng Token mới nhất tách ra để GitHub không chặn
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    BOT_TOKEN = "8835894291:" + "AAGFaumezRa9baMMlEispiCVxa7VQjFeAz4"

GROUP_ID = -1003939505873
CHANNEL_ID = -1003980680518
PRIVATE_GROUP_LINK = "https://t.me/+PMp4CC-Q0XczOThl"
PRIVATE_GROUP_ID = -1003939505873
ADMIN_ID = 8632660546

invite_data = {}
logging.basicConfig(level=logging.INFO)

def get_main_keyboard():
    nut_1 = InlineKeyboardButton("VAO NHOM KIN VIP", url=PRIVATE_GROUP_LINK)
    nut_2 = InlineKeyboardButton("LIEN HE AD", url="https://t.me/RNBNOTES")
    keyboard = [[nut_1], [nut_2]]
    return InlineKeyboardMarkup(keyboard)

async def dang_bai_20h(context: ContextTypes.DEFAULT_TYPE):
    text = "Bai cau toi 20h - My da khoanh chi tiet trong nhom rieng."
    try:
        msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=get_main_keyboard())
        await context.bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=msg.message_id, disable_notification=True)
    except Exception as e:
        print(f"Loi dang bai: {e}")

async def chao_thanh_vien_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_member.status == ChatMemberStatus.MEMBER:
        new_user = update.chat_member.new_chat_member.user
        try:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Chao {new_user.mention_html()} da vao nhom cua My! Nho doc ghim nhe!", parse_mode="HTML", reply_markup=get_main_keyboard())
        except:
            pass
        inviter = update.chat_member.from_user
        if inviter.id != new_user.id:
            invite_data[inviter.id] = invite_data.get(inviter.id, 0) + 1

async def auto_reply_tu_dong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    txt = update.message.text.lower()
    if "cau" in txt:
        await update.message.reply_text("My gui cau chi tiet trong nhom kin roi:", reply_markup=get_main_keyboard())
    elif "nhom" in txt or "link" in txt:
        await update.message.reply_text(f"Link nhom kin day: {PRIVATE_GROUP_LINK}", reply_markup=get_main_keyboard())

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and update.message.reply_to_message:
        await context.bot.ban_chat_member(update.effective_chat.id, update.message.reply_to_message.from_user.id)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id
    if args and args[0].startswith("ref_"):
        try:
            inviter_id = int(args[0].replace("ref_", ""))
            invite_data[inviter_id] = invite_data.get(inviter_id, 0) + 1
            await update.message.reply_text(f"Cam on ban! Link nhom kin: {PRIVATE_GROUP_LINK}", reply_markup=get_main_keyboard())
        except:
            pass
    else:
        my_ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        await update.message.reply_text(f"Link moi rieng cua ban:\n{my_ref_link}\nDiem: {invite_data.get(user_id, 0)}", reply_markup=get_main_keyboard())

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not invite_data:
        await update.message.reply_text("Chua co ai moi!")
        return
    top_sorted = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "TOP MOI BAN BE:\n" + "\n".join([f"- ID {uid}: {count} nguoi" for uid, count in top_sorted])
    await update.message.reply_text(text)

def main():
    print(f"Bot Token lay tu ENV: {BOT_TOKEN[:12]}...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(ChatMemberHandler(chao_thanh_vien_moi, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply_tu_dong))
    job = app.job_queue
    if job:
        job.run_daily(dang_bai_20h, time=time(hour=13, minute=0))
    print("Bot dang chay OK! - Da lay Token tu Environment")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
