import requests
from config import DISCORD_WEBHOOK_URL


def get_impact_color(impact_level):
    if "High" in impact_level:
        return 0xFF0000  # แดง
    elif "Medium" in impact_level:
        return 0xFFA500  # ส้ม
    elif "Low" in impact_level:
        return 0xFFFF00  # เหลือง
    else:
        return 0x00FF00  # เขียว

def format_embed(data):
    news = data["original_news"]

    color = get_impact_color(data["gemini_impact_level"])

    embed = {
        "title": f"{data['emoji']} {news.get('event', 'N/A')}",
        "description": f"📊 {data['summary']}",
        "color": color,
        "fields": [
            {
                "name": "💱 Currency",
                "value": news.get("currency", "N/A"),
                "inline": True
            },
            {
                "name": "📈 Impact",
                "value": data["gemini_impact_level"],
                "inline": True
            },
            {
                "name": "📊 Actual",
                "value": news.get("actual", "N/A"),
                "inline": True
            },
            {
                "name": "📉 Forecast",
                "value": news.get("forecast", "N/A"),
                "inline": True
            },
            {
                "name": "📅 Previous",
                "value": news.get("previous", "N/A"),
                "inline": True
            }
        ],
        "footer": {
            "text": "Forex News Bot"
        }
    }

    return embed

def send_to_discord_embed(embed):
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL is not configured.")
        return

    payload = {
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Embed sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending embed: {e}")

def test_embed():
    embed = {
        "title": "🟡 Test News Event",
        "description": "📊 นี่คือข้อความทดสอบจากบอทของคุณ",
        "color": 0xFFFF00,
        "fields": [
            {"name": "💱 Currency", "value": "USD", "inline": True},
            {"name": "📈 Impact", "value": "Low", "inline": True},
            {"name": "📊 Actual", "value": "1.2%", "inline": True},
            {"name": "📉 Forecast", "value": "1.0%", "inline": True},
            {"name": "📅 Previous", "value": "0.8%", "inline": True}
        ],
        "footer": {
            "text": "Forex News Bot"
        }
    }

    payload = {
        "embeds": [embed]
    }

    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == '__main__':
    # Example usage
    test_message = "Hello from your Forex Factory News Bot! This is a test message. 🟡"
    test_embed()
