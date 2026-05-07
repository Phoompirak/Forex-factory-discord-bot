# Forex Factory Discord Bot

บอทนี้ดึงข่าวเศรษฐกิจจาก Forex Factory เพื่อนำส่งเป็นข้อความ Discord embed อัตโนมัติตามเวลาที่กำหนดใน GitHub Actions.

## คุณสมบัติ

- ดึง `goldusd` market page จาก Forex Factory
- ประมวลผลข่าวด้วย Google Gemini API
- ส่งข้อความผ่าน Discord Webhook
- รันอัตโนมัติ 3 รอบต่อวันตามเวลาไทย:
  - 09:00 น.
  - 13:50 น.
  - 18:50 น.
- รองรับการรันผ่าน GitHub Actions พร้อม opt-in Node.js 24

## โครงสร้างโปรเจกต์

- `main.py` - ตัวเรียกใช้งานหลักของบอท
- `scraper.py` - ดึงข้อมูลข่าว / feed จาก Forex Factory
- `gemini_processor.py` - ประมวลผลเนื้อหาด้วย Gemini API
- `discord_sender.py` - สร้างและส่ง Discord embeds
- `config.py` - อ่านค่า environment variables
- `requirements.txt` - ไลบรารีที่ต้องติดตั้ง
- `.github/workflows/run_bot.yml` - workflow สำหรับ GitHub Actions

## ติดตั้งและใช้งาน

1. สร้าง virtualenv และติดตั้ง dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. สร้างไฟล์ `.env` หรือกำหนด environment variables:

```env
GEMINI_API_KEY=your_gemini_api_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

> อย่า commit ไฟล์ `.env` ขึ้น GitHub โดยตรง เพราะมีข้อมูลลับ

3. รันบอทด้วยคำสั่ง:

```bash
python main.py
```

## อัปโหลดขึ้น GitHub

1. สร้าง repository ใหม่บน GitHub
2. ทำการ commit และ push โค้ด:

```bash
git init
git add .
git commit -m "Initial Forex Factory Discord Bot setup"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

3. เพิ่ม Secrets ใน GitHub repository:

- `DISCORD_WEBHOOK_URL`
- `GEMINI_API_KEY`

4. ตรวจสอบ `.github/workflows/run_bot.yml` ว่าอยู่ใน branch `main`

## GitHub Actions

Workflow อยู่ที่: `.github/workflows/run_bot.yml`

- ทำงานอัตโนมัติแบบ schedule ตามเวลาไทย
- อาศัย `workflow_dispatch` เพื่อรันด้วยตนเองได้
- ตั้งค่า `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` เพื่อให้ GitHub Actions ใช้ Node.js 24
- ต้องตั้งค่า Secrets:
  - `DISCORD_WEBHOOK_URL`
  - `GEMINI_API_KEY`

## เวลา schedule ใน workflow

- `09:00 น.` เวลาไทย = `02:00 UTC`
- `13:50 น.` เวลาไทย = `06:50 UTC`
- `18:50 น.` เวลาไทย = `11:50 UTC`

## หมายเหตุ

- หากต้องการแก้ workflow ในอนาคต ให้ตรวจสอบเวอร์ชันของ actions ว่ายังรองรับ Node.js 24 อยู่หรือไม่
- ถ้า GitHub เปลี่ยน default เป็น Node.js 24 แล้ว สามารถลบค่า env `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` ได้
