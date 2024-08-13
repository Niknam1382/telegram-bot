import requests
import logging
import asyncio
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import jdatetime
import pytz

# اطلاعات کلیدی
CHANNEL_ID = "@ir_tehran_weather"
WEATHER_API_KEY = "b8a51132a36f4636911101626241208"
TELEGRAM_BOT_TOKEN = "7199265167:AAHRWNMZzvQaDTcHiee6lAjuqBTiQL2DIgk"
CITY_NAME = "Tehran"
DAYS = 5

def get_iran_time():
    iran_tz = pytz.timezone('Asia/Tehran')
    iran_now = datetime.now(iran_tz)
    iran_jdate = jdatetime.datetime.fromgregorian(datetime=iran_now)
    iran_time_str = iran_jdate.strftime('%Y/%m/%d   -   %H:%M:%S')
    return '⏱️ ' + iran_time_str

def get_weather():
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={CITY_NAME}&days={DAYS}&lang=fa"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # بررسی وضعیت HTTP
        data = response.json()

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

        days_naming = {
            1: "فردا",
            2: "پس‌ فردا",
            3: "سه روز بعد",
            4: "چهار روز بعد",
            5: "پنج روز بعد",
        }

        current = data["current"]
        forecast = data["forecast"]["forecastday"]

        conditions = "\n".join(
            [
                f"{days_naming[i+1]} - دمای متوسط: {day['day']['avgtemp_c']} درجه سانتی‌گراد - وضعیت هوا: {translation_dict.get(day['day']['condition']['text'], day['day']['condition']['text'])}"
                for i, day in enumerate(forecast)
            ]
        )

        output = (
            f"🌡️ دمای فعلی: {current['temp_c']} درجه سانتی‌گراد\n"
            f"⛅ وضعیت هوا: {translation_dict.get(current['condition']['text'], current['condition']['text'])}\n"
            f"💧 رطوبت: {current['humidity']}%\n"
            f"🌪️ سرعت باد: {current['wind_kph']} کیلومتر بر ساعت\n\n"
            f"⁉️ پیش‌بینی:\n{conditions}"
        )

        message = (
            f"{output}\n\n{get_iran_time()}\n🌥️ {CHANNEL_ID}"
        )
        return message
    
    except requests.exceptions.RequestException as e:
        logging.error(f"خطا در دریافت اطلاعات آب و هوا: {e}")
        return "خطا در دریافت اطلاعات آب و هوا."

# تابع برای ارسال پیام به کانال تلگرام
async def send_weather():
    message = get_weather()
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        logging.info("پیام با موفقیت به کانال ارسال شد.")
    except Exception as e:
        logging.error(f"خطای غیرمنتظره در ارسال پیام: {e}")

def main():
    scheduler = AsyncIOScheduler()

    # اجرای تابع send_weather هر 2 ساعت یک‌بار
    scheduler.add_job(send_weather, "interval", seconds=7200)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()