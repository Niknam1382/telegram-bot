import requests
import logging
from telegram import Bot
from telegram.ext import Application, ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# تنظیمات لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# توکن بات تلگرام
TELEGRAM_TOKEN = '7199265167:AAHRWNMZzvQaDTcHiee6lAjuqBTiQL2DIgk'
CHANNEL_ID = '@ir_tehran_weather'

# API Key از OpenWeatherMap
WEATHER_API_KEY = 'c98eb50389c22cd88756d85efb8b4df1'
CITY_ID = '112931'  # ID شهر تهران در OpenWeatherMap

# تابع برای تنظیم درخواست با Retry و Timeout
def requests_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# تابع برای دریافت اطلاعات آب و هوا
def get_weather():
    session = requests_session()
    url = f"http://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    response = session.get(url)
    data = response.json()
    
    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        message = f"آب و هوای تهران:\n\nوضعیت: {weather}\nدما: {temp}°C\nرطوبت: {humidity}%"
        return message
    else:
        logging.error(f"خطا در دریافت اطلاعات آب و هوا: {response.status_code} - {response.text}")
        return "خطا در دریافت اطلاعات آب و هوا."

# تابع برای ارسال پیام به کانال تلگرام
async def send_weather(application):
    message = get_weather()
    try:
        await application.bot.send_message(chat_id=CHANNEL_ID, text=message)
    except Exception as e:
        logging.error(f"خطا در ارسال پیام به تلگرام: {e}")

# راه‌اندازی ربات تلگرام
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    scheduler = AsyncIOScheduler()

    # ارسال اطلاعات آب و هوا هر دو ساعت یک بار
    scheduler.add_job(send_weather, 'interval', hours=2, args=[application])
    scheduler.start()

    # شروع ربات
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())