# app.py - โค้ดที่ปรับปรุงและใส่ Key/ID โดยตรง (Hardcoded)
import os
import json
import logging
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters, CommandHandler
from flask import Flask, request
import gspread

# ----------------- การตั้งค่าตัวแปรและ Logging (Hardcoded) -----------------

# *** คำเตือน: ข้อมูลเหล่านี้ถูก Hardcode เพื่อความรวดเร็ว แต่ควรใช้ Environment Variables ใน Production ***

TELEGRAM_TOKEN = "7691692707:AAEKyr9i-CxHDSm_NA5qD8skqjkvUCO1d5E"
SHEET_ID = "1nulgbPOAUeDBTzm9tdhym08rpDqpoD0lj_8ebRRO1Cs"

# JSON Key ของ Service Account ที่นำมาวางโดยตรง
# Python สามารถจัดการข้อความหลายบรรทัดที่มีเครื่องหมายคำพูดได้
SERVICE_ACCOUNT_JSON_STR = """
{
  "type": "service_account",
  "project_id": "telegram-expense-bot-479904",
  "private_key_id": "240d44b199f427a84a432298bd68aec7f8b1f2ea",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEugIBADANBgkqhkiG9w0BAQEFAASCBKQwggSgAgEAAoIBAQCgmkwvaDYQI7BY\nzb9UC8EH+3fQ9nd0Nq7WxpwziUV5VWaNvhR3UqvoROKfqYvvg5UQGBAHDaHu04Tm\nu41PGPoMc44CBp0daw0XE1mrpxMlslDc2GAdWLHtQBFBvkl/ZAAH7E27jgmsgE9j\nM+9OtJmEU1g4AIl9XUAEs6e01GiRPbzDto0gFRLuKI9nfqxFP7CBTASd1DS8CvJr\nS9p982WbbOWAj/1s1s+nQCT0/+K1wl4YQPKCI9InGTV4i+627IjTXJKUQ/G7hfW+\nhDcjqWbk0q1dzAw/1gPznG+U0afe1CZCTEGtEkoLkNCDwBp/uWv2+YLxsTneQrSk\nAo8gJrqRAgMBAAECgf8EHN5esgXh5g7l75qklD3PzH4CqBMcYQGUhABCbcNrZyuC\nVAZB70HOWhWsy7YHw2/T+yzBhpqeybK5GcL3Mk4KTkFwPp2shfXN9P7ET05PtrAD\n988WMig739UnfJ8LMLHVe0gcxhsYdfr1dSieQtQRJkOXLUGtb7WuppTzl9g6X+h8\nq6WCEST3HeiLWTn7F9AUNpdQ0km3JDwnH/f4dG6MGOlfJ458sJqiq2ogkvFPYvxs\nSGcBu/mqYakHCBWVblnL4fog/pqQhE4Zo+yN6m8vut52UyH5tWC9wAzV+MZBKQVU\ntFBxpAYR5Farx5rJUa1ouruYnZ8S8Ad7qnQVdeECgYEA2bzeXpJPIhMKnyIxke5d\njqEjCO6Rs/fqgO62Vxm3XX5dQIbIxPoKoageNV14FHusgn5BzY7M8pQbj9y8HhQ5\nvpVMeHtLN9kQbWUzpXDkrF/+caTBYFwanAfqBR+O2x2pvO2kEKePt66v6s5LnYBK\nruU+CJDtnFUKUehXvYgf8XECgYEAvNMoOc3GfsayzNp1laEQQ3IhXf/MVYrlj+/Z\noR5EVd7xCQNNIORPHRi7CrEyW8AVrvgeHBUmcCkRI77y/Mg8fb1TGRdQawqwgzpa\nMzYk8FIX3nDh/4vS1gSRVX6Ggeye7UYBtRu0c9DL3w1qgWFNVX+V2gaea2cXZOL5\naS7UyyECgYBoRbuUPKrq3YWTqdNlWGqzeFWH3IAoUOMLtcXatnUKsA5GbYXOVxQq\nUJGO6uErpgJ6R66Jm15ouSbt4T6xhOwWafdCJ4FhEHF+gh2WmBbauennUIhO9izE\nFkIrC+7k3jLASGnuk+AOjfivEPZDSgH5+cyYW5d/63bSvNrv6DWr8QKBgA7SJB4l\nYKciwXYCz6fm9HfWxXezVD6CoHIjyVk0Hvj+frzOXYdvZCZMgqHcNq+s7AbHwtVB\nc7rp/kZn/nqI3PahnZwikFVWiXRDaEEMxul2CBmVkqeUOgBCa4XiYHxiLjdBf3DP\ns+JDST1AuFNfZ8qGMSTj0BtuBBAPILR40IsBAoGAQ5olg1wSuSrin/FS251ShFAN\nRc0OoyMt42vHgZRrn114qTgR46y59lu/WNFkshk2X+TEvikrBaI95ur8BHiWBYZD\nbHuleI/mRe7BtXwtPAJXej+ZSzy/fHycnDvFrLghG/BB3X2yxfHu70kI8ea8xmqz\nN3ms7e0YuowL+Vv5FeA=\n-----END PRIVATE KEY-----\n",
  "client_email": "savingmange@telegram-expense-bot-479904.iam.gserviceaccount.com",
  "client_id": "110205949146900883161",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/savingmange%40telegram-expense-bot-479904.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----------------- ฟังก์ชันจัดการ Google Sheets -----------------

def get_sheets_client():
    """สร้าง Client สำหรับเชื่อมต่อ Google Sheets โดยใช้ JSON Key String"""
    if not SERVICE_ACCOUNT_JSON_STR:
        logger.error("SERVICE_ACCOUNT_JSON_KEY is missing (should not happen if hardcoded).")
        return None
        
    try:
        credentials_json = json.loads(SERVICE_ACCOUNT_JSON_STR)
        gc = gspread.service_account_from_dict(credentials_json)
        # ใช้ .worksheet('Sheet1') ถ้าคุณไม่ได้เปลี่ยนชื่อแท็บ
        return gc.open_by_key(SHEET_ID).sheet1 
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets. Check SHEET_ID or JSON format: {e}")
        return None

def append_to_sheet(data_list):
    """บันทึกข้อมูลเป็นแถวใหม่"""
    try:
        worksheet = get_sheets_client()
        if worksheet:
            # เพิ่มข้อมูล
            worksheet.append_row(data_list)
            return True
        return False
    except Exception as e:
        logger.error(f"Error appending row to Google Sheets: {e}")
        return False

# ----------------- ฟังก์ชันจัดการ Telegram Handlers -----------------

async def start(update: Update, context):
    """ตอบกลับคำสั่ง /start"""
    await update.message.reply_text("👋 สวัสดี! โปรดใช้รูปแบบ: **/จ่าย [จำนวนเงิน] [รายการ]** หรือ **/รับ [จำนวนเงิน] [รายการ]**", parse_mode='Markdown')

async def handle_text(update: Update, context):
    """ประมวลผลข้อความที่ได้รับ (สำหรับการบันทึก)"""
    text = update.message.text
    
    try:
        parts = text.split(maxsplit=2)
        command = parts[0].lower()
        
        if command in ("/จ่าย", "/รับ") and len(parts) >= 3:
            transaction_type = "รายจ่าย" if command == "/จ่าย" else "รายรับ"
            amount = float(parts[1])
            description = parts[2]
            
            record = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                transaction_type,
                description,
                amount,
                "" # ช่องว่างสำหรับลิงก์สลิป
            ]
            
            if append_to_sheet(record):
                response = f"✅ บันทึก **{transaction_type}** {amount:,.2f} บาท ({description}) เรียบร้อยแล้ว"
            else:
                response = "❌ บันทึกไม่สำเร็จ โปรดตรวจสอบการตั้งค่า Sheets และ Service Account"
        else:
            response = "⚠️ รูปแบบไม่ถูกต้อง โปรดใช้: **/จ่าย [จำนวนเงิน] [รายการ]**"
    
    except ValueError:
        response = "🚫 จำนวนเงินไม่ถูกต้อง โปรดใส่ตัวเลข"
    except Exception as e:
        logger.error(f"Unhandled error in handle_text: {e}")
        response = f"⚠️ เกิดข้อผิดพลาดภายใน: {e}"
        
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_photo(update: Update, context):
    """จัดการรูปภาพสลิป"""
    await update.message.reply_text("รูปภาพถูกรับแล้ว แต่การอ่านสลิปอัตโนมัติ (OCR/AI) ยังต้องพัฒนาเพิ่มเติมในโค้ด")


# ----------------- การตั้งค่า Web Server (Flask) -----------------

# ใช้ Flask เพื่อรับ Webhook
app = Flask(__name__)
bot = Bot(TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None)

# เพิ่ม Handlers ให้กับ Dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
dispatcher.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.route('/', methods=['POST'])
async def webhook_handler():
    """
    ฟังก์ชัน Webhook หลักที่รับ POST Request จาก Telegram
    """
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        await dispatcher.process_update(update)
    return 'ok'

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint สำหรับ Cloud Run"""
    return "Bot is running!", 200

# ----------------- การรัน Gunicorn (แก้ไขปัญหา PORT) -----------------

# โค้ดนี้จะถูกรันโดย Gunicorn ผ่านไฟล์ Procfile
# ดังนั้นจึงไม่จำเป็นต้องมี if __name__ == '__main__': app.run()