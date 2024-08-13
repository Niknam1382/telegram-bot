import requests
import logging
import asyncio
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import jdatetime
import pytz

def get_iran_time():
    iran_tz = pytz.timezone('Asia/Tehran')
    iran_now = datetime.now(iran_tz)
    iran_jdate = jdatetime.datetime.fromgregorian(datetime=iran_now)
    iran_time_str = iran_jdate.strftime('%Y/%m/%d   -   %H:%M:%S')
    return '⏱️ ' + iran_time_str










CHANNEL_ID = "@ir_tehran_weather"
WEATHER_API_KEY = "c98eb50389c22cd88756d85efb8b4df1"
CITY_ID = "112931"


def get_weather():
    # API Key خود را اینجا وارد کنید
    api_key = "b8a51132a36f4636911101626241208"
    city = "Tehran"
    days = 2  # تعداد روزهایی که می‌خواهید پیش‌بینی شود
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days={days}&lang=fa"

    response = requests.get(url)
    data = response.json()

    # دیکشنری برای ترجمه کلمات انگلیسی به فارسی
    translation_dict = {
        "Sunny": "آفتابی",
        "Patchy rain nearby": "باران پراکنده در نزدیکی",
        "Clear": "صاف",
        "Cloudy": "ابری",
        "Overcast": "ابری کامل",
        "Rain": "باران",
        "Thunderstorm": "طوفان رعد و برق",
        "Partly cloudy": "نیمه ابری",
    }

    # دیکشنری برای نام‌گذاری روزها
    days_naming = {
        1: "فردا",
        2: "پس‌ فردا",
    }

    if "error" not in data:
        current = data["current"]
        forecast = data["forecast"]["forecastday"]

        conditions = "\n".join(
            [
                f"{days_naming[i+1]} - دمای متوسط: {day['day']['avgtemp_c']} درجه سانتی‌گراد - وضعیت هوا: {translation_dict.get(day['day']['condition']['text'], day['day']['condition']['text'])}"
                for i, day in enumerate(forecast)
            ]
        )

        output = (
            f"دمای فعلی: {current['temp_c']} درجه سانتی‌گراد\n"
            f"وضعیت هوا: {translation_dict.get(current['condition']['text'], current['condition']['text'])}\n"
            f"رطوبت: {current['humidity']}%\n"
            f"سرعت باد: {current['wind_kph']} کیلومتر بر ساعت\n\n"
            f"پیش‌بینی:\n{conditions}"
        )

        message = (
            f"{output}\n\n{get_iran_time()}\n🌥️ @ir_tehran_weather"
        )
        return message
    else:
        logging.error(
            f"خطا در دریافت اطلاعات آب و هوا: {response.status_code} - {response.text}"
        )
        return "خطا در دریافت اطلاعات آب و هوا."

# تابع برای ارسال پیام به کانال تلگرام
async def send_weather():
    message = get_weather()
    bot = telegram.Bot(token="7199265167:AAHRWNMZzvQaDTcHiee6lAjuqBTiQL2DIgk")
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        logging.info("Your Message Send To Channel")
    except Exception as e:
        logging.error(f"Unxpected Error On Send_weather: {e}")

def main():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_weather, "interval", seconds=7200)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()