import aiohttp
import logging
import asyncio
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import jdatetime
import os
import pytz

def get_iran_time():
    iran_tz = pytz.timezone('Asia/Tehran')
    iran_now = datetime.now(iran_tz)
    iran_jdate = jdatetime.datetime.fromgregorian(datetime=iran_now)
    iran_time_str = iran_jdate.strftime('%Y/%m/%d   -   %H:%M:%S')
    return '⏱️ ' + iran_time_str

# تنظیمات لاگینگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# تنظیمات
TEHRAN_CITY_ID = "112931"  # شناسه شهر تهران
QOM_CITY_ID = "119208"  # شناسه شهر قم
MASHHAD_CITY_ID = "124665"  # شناسه شهر مشهد
TEHRAN_CHANNEL_ID = "@ir_tehran_weather"  # کانال تلگرامی آب و هوای تهران
QOM_CHANNEL_ID = "@ir_qom_weather"  # کانال تلگرامی آب و هوای قم
MASHHAD_CHANNEL_ID = "@ir_mashhad_weather"  # کانال تلگرامی آب و هوای مشهد
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "c98eb50389c22cd88756d85efb8b4df1")  # کلید API آب و هوا
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7199265167:AAHRWNMZzvQaDTcHiee6lAjuqBTiQL2DIgk")  # توکن ربات تلگرام

async def get_weather(city_id):
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                utc_time = datetime.utcfromtimestamp(data['dt'])
                city = data['name']
                weather = data['weather'][0]['description']
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                cloud_all = data['clouds']['all']
                visibility = data['visibility']

                time = get_iran_time()

                if city == 'تهران':
                    x = 'tehran'
                elif city == 'قم':
                    x = 'qom'
                else:
                    x = 'mashhad'
                message = (
                    f"آب و هوای {city}:\n\nوضعیت: {weather}\nدما: {temp} درجه سانتیگراد\nرطوبت: %{humidity}\nسرعت وزش باد: {wind_speed} m/s\nمیزان ابر: %{cloud_all}\nمیدان دید: {visibility} متر\n\n{time}\n🌥️ @ir_{x}_weather"
                )
                return message
            else:
                logging.error(f"خطا در دریافت اطلاعات آب و هوا: {response.status} - {await response.text()}")
                return "خطا در دریافت اطلاعات آب و هوا."

async def send_weather(city_id, channel_id):
    message = await get_weather(city_id)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(chat_id=channel_id, text=message)
        logging.info(f"پیام شما به کانال {channel_id} ارسال شد")
    except Exception as e:
        logging.error(f"خطای غیرمنتظره در send_weather: {e}")

async def main():
    scheduler = AsyncIOScheduler()

    # ارسال آب و هوای تهران به کانال مربوطه
    scheduler.add_job(send_weather, "interval", seconds=300, args=[TEHRAN_CITY_ID, TEHRAN_CHANNEL_ID])
    # ارسال آب و هوای قم به کانال مربوطه
    scheduler.add_job(send_weather, "interval", seconds=300, args=[QOM_CITY_ID, QOM_CHANNEL_ID])
    # ارسال آب و هوای مشهد به کانال مربوطه
    scheduler.add_job(send_weather, "interval", seconds=300, args=[MASHHAD_CITY_ID, MASHHAD_CHANNEL_ID])

    scheduler.start()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main())
