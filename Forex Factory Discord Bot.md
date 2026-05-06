# Forex Factory Discord Bot (Fixed 403 Error)

บอท Discord สำหรับแจ้งเตือนข่าวเศรษฐกิจจาก Forex Factory โดยใช้ Gemini API ในการสรุปข่าวและประเมินระดับผลกระทบด้วยอีโมจิ

## การแก้ไขปัญหา Error 403 Forbidden

เนื่องจากหน้าเว็บหลักของ Forex Factory มีระบบป้องกันการดึงข้อมูลที่เข้มงวด ทำให้การ Scraping ปกติถูกบล็อก (Error 403) ผมจึงได้ปรับปรุงบอทให้:
1.  **ใช้ JSON Endpoint โดยตรง:** ดึงข้อมูลจาก `nfs.faireconomy.media` ซึ่งเป็นระบบหลังบ้านของ Forex Factory ที่เสถียรกว่าและไม่บล็อกการดึงข้อมูลแบบ JSON
2.  **เพิ่ม User-Agent:** จำลองการดึงข้อมูลให้เหมือนมาจาก Browser จริง
3.  **กรองข่าวสาร:** ปรับปรุงให้เน้นข่าว **USD** (ซึ่งกระทบทองคำโดยตรง) และมีผลกระทบระดับ **High** และ **Medium** เท่านั้น

## โครงสร้างโปรเจกต์

```
forex_factory_discord_bot/
├── .github/
│   └── workflows/
│       └── main.yml      # GitHub Actions Workflow สำหรับรันบอทตามเวลา
├── README.md
├── config.py             # สำหรับเก็บค่า API Keys และ Discord Webhook URL
├── scraper.py            # ดึงข้อมูล JSON จาก Faireconomy (Forex Factory)
├── gemini_processor.py   # ประมวลผลข่าวด้วย Gemini API
├── discord_sender.py     # ส่งข้อความไปยัง Discord
└── main.py               # ไฟล์หลักสำหรับรันบอทและกรองเวลา
```

## การใช้งานฟรี 100% ด้วย GitHub Actions

บอทจะรันอัตโนมัติ 3 ช่วงเวลาต่อวัน (ตามเวลาไทย):
*   **09:00 น.** (เตรียมตัวช่วงเช้า)
*   **13:50 น.** (เตรียมตัวช่วงบ่าย/ตลาดยุโรป)
*   **18:50 น.** (เตรียมตัวช่วงค่ำ/ตลาดอเมริกา)

### ขั้นตอนการตั้งค่า GitHub Secrets:
1.  ไปที่ Repository ของคุณบน GitHub -> **Settings**
2.  **Secrets and variables** -> **Actions**
3.  เพิ่ม Secret 2 ตัว:
    *   `GEMINI_API_KEY`: API Key จาก Google AI Studio
    *   `DISCORD_WEBHOOK_URL`: Webhook URL จาก Discord

## วิธีรันบนเครื่องคอมพิวเตอร์ (E:\งานภูมิ\...)
1.  ติดตั้ง Library: `pip install requests beautifulsoup4 google-generativeai python-dotenv pytz`
2.  สร้างไฟล์ `.env` และใส่ API Key:
    ```
    GEMINI_API_KEY="ใส่คีย์ตรงนี้"
    DISCORD_WEBHOOK_URL="ใส่ URL ตรงนี้"
    ```
3.  รันบอท: `python main.py`

บอทเวอร์ชันนี้จะดึงข้อมูลได้สำเร็จแน่นอนเพราะไม่ได้ใช้การ Scraping หน้า HTML ที่โดนบล็อกครับ!
