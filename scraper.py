import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def scrape_forex_factory(url=None):
    # ใช้ JSON endpoint ของ Forex Factory โดยตรง ซึ่งเสถียรกว่าและดึงข้อมูลได้ง่ายกว่า
    # ข้อมูลนี้จัดทำโดย Faireconomy (บริษัทแม่ของ Forex Factory)
    json_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.forexfactory.com/"
    }

    news_data = None
    if url:
        print(f"Fetching Forex Factory market page from {url}...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            show_more = soup.select_one(
                "#ls-layout > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div > div.foot > ul > li > a:nth-child(2)"
            )
            if show_more and show_more.get("href"):
                more_url = urllib.parse.urljoin(url, show_more["href"])
                print(f"Found expanded market link: {more_url}")
                response = requests.get(more_url, headers=headers)
                response.raise_for_status()
                if "application/json" in response.headers.get("Content-Type", ""):
                    news_data = response.json()
                    print("Loaded expanded feed from market page.")
                else:
                    print("Expanded market URL did not return JSON; falling back to calendar JSON endpoint.")
            else:
                print("Show-more link not found on market page; falling back to calendar JSON endpoint.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market page or expanded feed: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from expanded market feed: {e}")

    if news_data is None:
        try:
            print(f"Fetching news from {json_url}...")
            response = requests.get(json_url, headers=headers)
            response.raise_for_status()
            news_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching JSON from {json_url}: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []

    news_items = []
    # กรองเฉพาะข่าวที่เกิดขึ้นในวันนี้ (หรือข่าวล่าสุด)
    current_date = datetime.utcnow().date()
    
    for item in news_data:
        # แปลงเวลาจาก ISO 8601 (เช่น 2024-05-06T09:00:00-04:00)
        try:
            # ดึงเฉพาะส่วนวันที่มาเปรียบเทียบ
            event_date_str = item.get('date', '').split('T')[0]
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            
            # เก็บเฉพาะข่าวของวันนี้ หรือคุณอาจจะปรับให้เก็บข่าวทั้งหมดของสัปดาห์ก็ได้
            # ในที่นี้ขอเก็บข่าวทั้งหมดของสัปดาห์เพื่อให้บอทสรุปตามช่วงเวลาที่รัน
            
            news_items.append({
                'time': item.get('date', 'N/A'),
                'currency': item.get('country', 'N/A'), # ใน JSON ใช้ country แทน currency (เช่น USD)
                'impact': item.get('impact', 'N/A'),
                'event': item.get('title', 'N/A'),
                'actual': item.get('actual', 'N/A'),
                'forecast': item.get('forecast', 'N/A'),
                'previous': item.get('previous', 'N/A')
            })
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue

    return news_items

if __name__ == '__main__':
    news = scrape_forex_factory()
    print(f"Found {len(news)} news items.")
    if news:
        print("Sample news item:", news[0])