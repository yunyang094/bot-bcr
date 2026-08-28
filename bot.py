import logging
import os
import base64
import json
from datetime import time, datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler, CallbackQueryHandler
import asyncio
BOT_TOKEN = os.getenv('BOT_TOKEN','')
if not BOT_TOKEN:
    BOT_TOKEN = '8835894291:AAGFaumezRa9baMMlEispiCVxa7VQjFeAz4'
GROUP_ID = -1003939505873
CHANNEL_ID = -1003980680518
PRIVATE_GROUP_LINK = 'https://t.me/+PMp4CC-Q0XczOThl'
LINK_LIEN_HE_AD = 'https://t.me/RNBNOTES'
ADMIN_ID = 8632660546
IMAGE_PATH = 'bai_toi_nay_20h.jpg'
LOGO_PATH = 'logo_bcr_transparent.png'
LICH_FILE = 'lich_1_tuan.json'
SCHEDULE_FOLDER = 'lich_1_tuan'
LOGO_B64=''
invite_data={}
logging.basicConfig(level=logging.WARNING)

def ensure_logo():
    pass

def get_main_keyboard(bot_username=None):
    link_bot = f'https://t.me/{bot_username}?start=thongke' if bot_username else 'https://t.me/doccaubcr_bot?start=thongke'
    nut_1 = InlineKeyboardButton('🔥 VÀO NHÓM KÍN VIP', url=PRIVATE_GROUP_LINK)
    nut_2 = InlineKeyboardButton('💬 LIÊN HỆ AD', url=LINK_LIEN_HE_AD)
    nut_3 = InlineKeyboardButton('📊 XEM THỐNG KÊ', url=link_bot)
    nut_4 = InlineKeyboardButton('🎁 QUAY THƯỞNG', callback_data='quay_thuong')
    return InlineKeyboardMarkup([[nut_1], [nut_2, nut_3], [nut_4]])

def add_logo_to_image(image_path):
    ensure_logo()
    try:
        from PIL import Image, ImageDraw
        if not os.path.exists(image_path) or not os.path.exists(LOGO_PATH): return
        board = Image.open(image_path).convert('RGBA')
        W,H = board.size
        logo = Image.open(LOGO_PATH).convert('RGBA')
        logo_size_corner = int(W*0.18)
        logo_corner = logo.resize((logo_size_corner, logo_size_corner), Image.LANCZOS)
        bg_size = int(logo_size_corner*1.15)
        bg = Image.new('RGBA',(bg_size,bg_size),(0,0,0,0))
        draw = ImageDraw.Draw(bg)
        draw.ellipse([0,0,bg_size-1,bg_size-1], fill=(255,255,255,230), outline=(0,0,0,200), width=2)
        x = W - bg_size - int(H*0.04)
        y = H - bg_size - int(H*0.04)
        board.alpha_composite(bg,(x,y))
        lx = x + (bg_size - logo_size_corner)//2
        ly = y + (bg_size - logo_size_corner)//2
        board.alpha_composite(logo_corner,(lx,ly))
        logo_size_center = int(W*0.38)
        logo_center = logo.resize((logo_size_center, logo_size_center), Image.LANCZOS)
        alpha = logo_center.split()[3]
        alpha = alpha.point(lambda p: int(p*0.32))
        logo_center.putalpha(alpha)
        cx = (W - logo_size_center)//2
        cy = (H - logo_size_center)//2
        board.alpha_composite(logo_center,(cx,cy))
        board.convert('RGB').save(image_path,'JPEG', quality=92)
    except Exception as e:
        print(f'Loi logo: {e}')

def get_bai_hom_nay():
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    if os.path.exists(LICH_FILE):
        try:
            with open(LICH_FILE,'r', encoding='utf-8') as f:
                lich=json.load(f)
                start_date=datetime.fromisoformat(lich.get('start_date'))
                days_passed=(datetime.now()-start_date).days
                if days_passed<0: days_passed=0
                index=days_passed%7+1
                img_path=os.path.join(SCHEDULE_FOLDER,f'bai_{index}.jpg')
                cap_path=os.path.join(SCHEDULE_FOLDER,f'bai_{index}.txt')
                if os.path.exists(img_path):
                    return img_path,cap_path
        except: pass
    for i in range(1,8):
        img_path=os.path.join(SCHEDULE_FOLDER,f'bai_{i}.jpg')
        cap_path=os.path.join(SCHEDULE_FOLDER,f'bai_{i}.txt')
        if os.path.exists(img_path):
            return img_path,cap_path
    return IMAGE_PATH,'caption.txt'

# --- FIX: nhan_anh_moi - handle both bai-1 and bai_1 ---
async def nhan_anh_moi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... existing admin check code ...
    if not update.message or not update.message.photo:
        return
    # Normalize filename: bai-1.jpg -> bai_1.jpg, bai-1.txt -> bai_1.txt
    raw_name = context.args[0] if context.args else "bai_1.jpg"
    fixed_name = raw_name.replace("-", "_")  # <- FIX chính
    # fixed_name giờ luôn là dạng bai_1, bai_2...
    file_path = os.path.join(SCHEDULE_FOLDER, fixed_name)
    os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(file_path)
    add_logo_to_image(file_path)
    await update.message.reply_text(f"✅ Đã lưu {fixed_name}")
