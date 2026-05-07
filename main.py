from scraper import scrape_forex_factory
from gemini_processor import process_news_with_gemini
from discord_sender import format_embed, send_to_discord_embed
from config import FOREX_FACTORY_URL
import time
from datetime import datetime, timezone
import pytz

def is_event_near_current_time(event_time_str, window_minutes=300):
    """
    ตรวจสอบว่าเวลาของข่าวอยู่ใกล้กับเวลาปัจจุบันหรือไม่ (ภายใน window_minutes)
    เพื่อให้บอทส่งเฉพาะข่าวที่เพิ่งเกิดขึ้นหรือกำลังจะเกิดขึ้น
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
    print(f"Starting Forex Factory Discord Bot at {datetime.now()}...")
    news_items = scrape_forex_factory(FOREX_FACTORY_URL)

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
