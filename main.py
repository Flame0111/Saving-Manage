# main.py - โค้ดสำหรับ Google Cloud Functions (GCF)
# GCF ใช้โมเดลการทำงานแบบ Serverless โดยมีฟังก์ชันเดียวที่รับ HTTP Request
# เราจะใช้ Bot.send_message() แทนการใช้ Dispatcher และ Context

import json
import logging
from datetime import datetime
from telegram import Bot, Update
from telegram.constants import ParseMode
import gspread
from google.cloud import secretmanager

# ----------------- การตั้งค่าตัวแปรและ Logging (Hardcoded) -----------------

# *** คำเตือน: ข้อมูลเหล่านี้ถูก Hardcode เพื่อความรวดเร็ว แต่ควรใช้ Environment Variables/Secret Manager ใน Production ***

TELEGRAM_TOKEN = "7691692707:AAEKyr9i-CxHDSm_NA5qD8skqjkvUCO1d5E"
SHEET_ID = "1nulgbPOAUeDBTzm9tdhym08rpDqpoD0lj_8ebRRO1Cs"

# JSON Key ของ Service Account ที่นำมาวางโดยตรง
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

WORKSHEET_NAME = "Sheet1" 
GLOBAL_SHEETS_CLIENT = None

def get_sheets_client():
    """สร้าง Client สำหรับเชื่อมต่อ Google Sheets แบบ Lazy Loading"""
    global GLOBAL_SHEETS_CLIENT
    
    if GLOBAL_SHEETS_CLIENT:
        return GLOBAL_SHEETS_CLIENT
        
    try:
        credentials_json = json.loads(SERVICE_ACCOUNT_JSON_STR)
        gc = gspread.service_account_from_dict(credentials_json)
        
        # เปิด Spreadsheet และ Worksheet
        spreadsheet = gc.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        GLOBAL_SHEETS_CLIENT = worksheet
        logger.info("Successfully connected to Google Sheets.")
        return worksheet
        
    except Exception as e:
        logger.error(f"GSPREAD ERROR: Failed to connect or access worksheet: {e}")
        return None 

def append_to_sheet(data_list):
    """บันทึกข้อมูลเป็นแถวใหม่"""
    try:
        worksheet = get_sheets_client()
        if worksheet:
            worksheet.append_row(data_list)
            return True
        return False
    except Exception as e:
        logger.error(f"Error appending row to Google Sheets: {e}")
        return False

# ----------------- ฟังก์ชันจัดการ Telegram Handlers (Synchronous) -----------------

def handle_start(bot: Bot, update: Update, chat_id: int):
    """ตอบกลับคำสั่ง /start"""
    message = "👋 สวัสดี! โปรดใช้รูปแบบ: **/จ่าย [จำนวนเงิน] [รายการ]** หรือ **/รับ [จำนวนเงิน] [รายการ]**"
    bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)

def handle_text_message(bot: Bot, update: Update, chat_id: int):
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
                response = "❌ บันทึกไม่สำเร็จ! กรุณาตรวจสอบว่า Service Account มีสิทธิ์ Editor ใน Google Sheet"
        else:
            response = "⚠️ รูปแบบไม่ถูกต้อง โปรดใช้: **/จ่าย [จำนวนเงิน] [รายการ]**"
    
    except ValueError:
        response = "🚫 จำนวนเงินไม่ถูกต้อง โปรดใส่ตัวเลข"
    except Exception as e:
        logger.error(f"Unhandled error in handle_text: {e}")
        response = f"⚠️ เกิดข้อผิดพลาดภายใน: {e}"
        
    bot.send_message(chat_id=chat_id, text=response, parse_mode=ParseMode.MARKDOWN)

def handle_photo_message(bot: Bot, update: Update, chat_id: int):
    """จัดการรูปภาพสลิป"""
    bot.send_message(chat_id=chat_id, text="รูปภาพถูกรับแล้ว แต่การอ่านสลิปอัตโนมัติ (OCR/AI) ยังต้องพัฒนาเพิ่มเติมในโค้ด")


# ----------------- GCF Entry Point -----------------

def telegram_webhook(request):
    """
    ฟังก์ชันหลักที่รับ HTTP Request จาก Telegram (Google Cloud Function Entry Point)
    """
    
    # 1. Health Check (GET Request)
    if request.method == "GET":
        return "Bot is running! (GCF)", 200

    # 2. Process Telegram Update (POST Request)
    if request.method == "POST":
        
        # รับ JSON body จาก Request
        request_data = request.get_json(silent=True)
        if not request_data:
            return 'No update data received', 200
            
        try:
            # สร้าง Update object
            bot_instance = Bot(TELEGRAM_TOKEN)
            update = Update.de_json(request_data, bot_instance)
        except Exception as e:
            logger.error(f"Error parsing update JSON: {e}")
            return 'Invalid update format', 200
            
        # ตรวจสอบประเภทของการ Update และเรียกใช้ Handler ที่เหมาะสม
        if update.message:
            chat_id = update.message.chat_id
            text = update.message.text
            photo = update.message.photo
            
            if text:
                # ตรวจสอบคำสั่ง /start
                if text.lower() == '/start':
                    handle_start(bot_instance, update, chat_id)
                
                # ตรวจสอบข้อความปกติ (สำหรับการบันทึก)
                elif not text.startswith('/'):
                    handle_text_message(bot_instance, update, chat_id)
                
            elif photo:
                handle_photo_message(bot_instance, update, chat_id)
                
        # ต้องคืนค่า HTTP 200 (OK) เสมอ เพื่อบอก Telegram ว่ารับข้อความแล้ว
        return 'ok', 200

    return 'Method not allowed', 405
