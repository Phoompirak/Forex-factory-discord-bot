from scraper import scrape_forex_factory
from gemini_processor import process_news_with_gemini
from discord_sender import format_embed, send_to_discord_embed
import time
from datetime import datetime, timedelta
import time
import pytz

def is_event_near_current_time(event_time_str, window_minutes=300):
    """
    ตรวจสอบว่าเวลาของข่าวอยู่ใกล้กับเวลาปัจจุบันหรือไม่ (ภายใน window_minutes)
    เพื่อให้บอทส่งเฉพาะข่าวที่เพิ่งเกิดขึ้นหรือกำลังจะเกิดขึ้น
    """
    try:
        # ตัวอย่างเวลาจาก JSON: 2024-05-06T09:00:00-04:00
        # ตัดส่วน Timezone ออกเพื่อความง่ายในการ parse เบื้องต้น
        clean_time_str = event_time_str[:19] 
        event_dt = datetime.strptime(clean_time_str, '%Y-%m-%dT%H:%M:%S')
        
        # ปรับเป็น UTC (สมมติว่าเวลาใน JSON เป็น UTC หรือใกล้เคียง)
        # หมายเหตุ: ในระบบจริงอาจต้องจัดการเรื่อง Timezone ให้แม่นยำกว่านี้
        now_utc = datetime.utcnow()
        
        # ถ้าเวลาข่าวห่างจากตอนนี้ไม่เกิน window_minutes (เช่น 5 ชั่วโมง เพื่อครอบคลุมช่วงเวลาที่รัน)
        diff = abs((now_utc - event_dt).total_seconds() / 60)
        return diff <= window_minutes
    except:
        return True # ถ้า parse ไม่ได้ ให้ส่งไปก่อนเพื่อความปลอดภัย

def run_bot():
    print(f"Starting Forex Factory Discord Bot at {datetime.now()}...")
    news_items = scrape_forex_factory()

    if not news_items:
        print("No news items found. Exiting.")
        return

    # กรองเฉพาะข่าวที่น่าสนใจ (เช่น USD หรือทองคำ) และมีผลกระทบ High/Medium
    # และกรองตามเวลาเพื่อให้ส่งเฉพาะข่าวในช่วงเวลานั้นๆ
    count = 0
    for news in news_items:
        # กรองเฉพาะข่าว USD (ซึ่งกระทบทองคำโดยตรง) และข่าวที่มีผลกระทบ
        if news['currency'] == 'USD' and news['impact'] in ['High', 'Medium']:
            
            # ตรวจสอบเวลา (เพื่อให้ส่งเฉพาะข่าวที่เกี่ยวข้องในช่วงที่รันบอท)
            if is_event_near_current_time(news['time']):
                processed_data = process_news_with_gemini(news)
                if processed_data:
                    message = (
                        f"{processed_data['emoji']} **{processed_data['gemini_impact_level']} Impact News!** {processed_data['original_news']['currency']} - {processed_data['original_news']['event']}\n"
                        f"Summary: {processed_data['summary']}\n"
                        f"Time: {processed_data['original_news']['time']} | Actual: {processed_data['original_news']['actual']} | Forecast: {processed_data['original_news']['forecast']} | Previous: {processed_data['original_news']['previous']}"
                    )
                    formatted_embed = format_embed(processed_data)
                    send_to_discord_embed(formatted_embed)
                    count += 1
                    time.sleep(1) 

    print(f"Forex Factory Discord Bot finished. Sent {count} notifications.")

if __name__ == '__main__':
    run_bot()
