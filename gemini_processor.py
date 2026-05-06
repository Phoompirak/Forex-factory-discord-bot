import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")

def get_impact_emoji(impact_level):
    if "High" in impact_level:
        return "🔴"
    elif "Medium" in impact_level:
        return "🟠"
    elif "Low" in impact_level:
        return "🟡"
    else:
        return "🟢" # No Impact or N/A

def process_news_with_gemini(news_item):
    event = news_item.get("event", "N/A")
    currency = news_item.get("currency", "N/A")
    impact = news_item.get("impact", "N/A")
    actual = news_item.get("actual", "N/A")
    forecast = news_item.get("forecast", "N/A")
    previous = news_item.get("previous", "N/A")

    prompt = f"""ใช้ภาษาไทยสรุป Summarize the following economic news event for a forex trader. \n\nEvent: {event}\nCurrency: {currency}\nImpact: {impact}\nActual: {actual}\nForecast: {forecast}\nPrevious: {previous}\n\nProvide a concise summary (1-2 sentences) and then state the impact level (High, Medium, Low, or No Impact) based on the provided impact. If the impact is N/A, assume No Impact. Example: 'Summary: ... Impact: High'"""

    try:
        response = model.generate_content(prompt)
        text_response = response.text

        summary_start = text_response.find("Summary:")
        impact_start = text_response.find("Impact:")

        summary = "N/A"
        gemini_impact_level = "N/A"

        if summary_start != -1 and impact_start != -1:
            summary = text_response[summary_start + len("Summary:"):impact_start].strip()
            gemini_impact_level = text_response[impact_start + len("Impact:"):].strip()
        elif summary_start != -1:
            summary = text_response[summary_start + len("Summary:"):].strip()
            gemini_impact_level = impact # Fallback to scraped impact if Gemini doesn't provide it clearly
        else:
            summary = text_response.strip()
            gemini_impact_level = impact # Fallback to scraped impact

        emoji = get_impact_emoji(gemini_impact_level)

        return {
            "original_news": news_item,
            "summary": summary,
            "gemini_impact_level": gemini_impact_level,
            "emoji": emoji
        }
    except Exception as e:
        print(f"Error processing news with Gemini: {e}")
        # Fallback if Gemini fails
        return {
            "original_news": news_item,
            "summary": f"Could not generate summary for: {event}",
            "gemini_impact_level": impact,
            "emoji": get_impact_emoji(impact)
        }

if __name__ == '__main__':
    # This is a placeholder for testing. In a real scenario, you'd get news from scraper.py
    sample_news = {
        'time': '08:30am',
        'currency': 'USD',
        'impact': 'High',
        'event': 'Non-Farm Employment Change',
        'actual': '272K',
        'forecast': '180K',
        'previous': '165K'
    }
    processed_data = process_news_with_gemini(sample_news)
    print(processed_data)

    sample_news_low = {
        'time': '10:00am',
        'currency': 'EUR',
        'impact': 'Low',
        'event': 'Industrial Production',
        'actual': '0.2%',
        'forecast': '0.1%',
        'previous': '0.0%'
    }
    processed_data_low = process_news_with_gemini(sample_news_low)
    print(processed_data_low)

    sample_news_na = {
        'time': '11:00am',
        'currency': 'JPY',
        'impact': 'N/A',
        'event': 'Bank Holiday',
        'actual': 'N/A',
        'forecast': 'N/A',
        'previous': 'N/A'
    }
    processed_data_na = process_news_with_gemini(sample_news_na)
    print(processed_data_na)
