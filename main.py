from scraper import scrape_forex_factory
from gemini_processor import process_news_with_gemini
from discord_sender import format_embed, send_to_discord_embed
from config import FOREX_FACTORY_URL
import time
import json
import os
from datetime import datetime, timezone, timedelta
import pytz

# ตั้งค่า Timezone เป็นไทย
BANGKOK_TZ = pytz.timezone('Asia/Bangkok')

SENT_NEWS_FILE = "sent_news.json"

def load_sent_news():
    if os.path.exists(SENT_NEWS_FILE):
        try:
            with open(SENT_NEWS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_sent_news(sent_news):
    with open(SENT_NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sent_news, f, ensure_ascii=False, indent=2)

def get_news_id(news):
    # สร้าง unique ID จากเวลาและชื่อข่าว
    return f"{news['time']}_{news['event']}"

def is_event_near_current_time(event_time_str, window_minutes=600):
    """
    ตรวจสอบว่าเวลาของข่าวอยู่ใกล้กับเวลาปัจจุบันหรือไม่
    เพิ่ม window เป็น 600 นาที (10 ชม.) เพื่อรองรับความล่าช้าของ GitHub Actions
    """
    try:
        event_dt = datetime.fromisoformat(event_time_str)
        if event_dt.tzinfo is None:
            event_dt = event_dt.replace(tzinfo=timezone.utc)
        
        now_utc = datetime.now(timezone.utc)
        diff = abs((now_utc - event_dt.astimezone(timezone.utc)).total_seconds() / 60)
        return diff <= window_minutes
    except Exception as e:
        print(f"Warning: unable to parse event time '{event_time_str}': {e}")
        return False

def run_bot():
    now_ict = datetime.now(BANGKOK_TZ)
    print(f"Starting Forex Factory Discord Bot at {now_ict.strftime('%Y-%m-%d %H:%M:%S')} (ICT)...")
    
    news_items = scrape_forex_factory(FOREX_FACTORY_URL)
    if not news_items:
        print("No news items found. Exiting.")
        return

    sent_news = load_sent_news()
    count = 0
    
    # กรองเฉพาะข่าวที่น่าสนใจ
    for news in news_items:
        # กรองเฉพาะข่าว USD และข่าวที่มีผลกระทบ High/Medium
        if news['currency'] == 'USD' and news['impact'] in ['High', 'Medium']:
            
            # ตรวจสอบเวลา (เพิ่ม window เพื่อความชัวร์)
            if is_event_near_current_time(news['time']):
                news_id = get_news_id(news)
                actual_val = news.get('actual', 'N/A')
                
                # ตรวจสอบว่าเคยส่งข่าวนี้ไปหรือยัง
                # เราจะส่ง 2 ครั้ง: 1. ตอนเป็น Forecast (Actual: N/A) และ 2. ตอนมี Actual แล้ว
                status_key = f"{news_id}_{'final' if actual_val != 'N/A' else 'preview'}"
                
                if status_key in sent_news:
                    continue # ข้ามถ้าเคยส่งสถานะนี้ไปแล้ว
                
                print(f"Processing new event: {news['event']} ({actual_val})")
                processed_data = process_news_with_gemini(news)
                
                if processed_data:
                    formatted_embed = format_embed(processed_data)
                    send_to_discord_embed(formatted_embed)
                    
                    # บันทึกสถานะว่าส่งแล้ว
                    sent_news[status_key] = {
                        "sent_at": now_ict.isoformat(),
                        "actual": actual_val
                    }
                    
                    # ถ้าส่งตัวจริงแล้ว (final) ให้ลบ preview ออกเพื่อประหยัดพื้นที่ (optional)
                    if actual_val != 'N/A':
                        sent_news.pop(f"{news_id}_preview", None)
                        
                    count += 1
                    time.sleep(1) 

    save_sent_news(sent_news)
    print(f"Forex Factory Discord Bot finished. Sent {count} new notifications.")

if __name__ == '__main__':
    run_bot()
