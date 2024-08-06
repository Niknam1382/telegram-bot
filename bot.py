import requests
import logging
import asyncio
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import jdatetime

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# تنظیمات
TEHRAN_CITY_ID = "112931"  # شناسه شهر تهران
QOM_CITY_ID = "119208"  # شناسه شهر قم
MASHHAD_CITY_ID = "124665"
TEHRAN_CHANNEL_ID = "@ir_tehran_weather"  # کانال تلگرامی آب و هوای تهران
QOM_CHANNEL_ID = "@ir_qom_weather"  # کانال تلگرامی آب و هوای 
MASHHAD_CHANNEL_ID = "@ir_mashhad_weather"
WEATHER_API_KEY = "c98eb50389c22cd88756d85efb8b4df1"

def get_weather(city_id):
    session = requests.session()
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    response = session.get(url)
    data = response.json()

    if response.status_code == 200:
        utc_time = datetime.utcfromtimestamp(data['dt'])
        city = data['name']
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        cloud_all = data['clouds']['all']
        visibility = data['visibility']

        now = jdatetime.datetime.now()
        time = f"{now.strftime('%Y/%m/%d    %H:%M:%S')}"
        if city == 'تهران':
            x = 'tehran'
        elif city == 'قم':
            x = 'qom'
        else:
            x = 'mashhad'
        message = (
            f"آب و هوای {city}:\n\nوضعیت: {weather}\nدما: {temp} درجه سانتیگراد\nرطوبت: %{humidity}\nسرعت وزش باد: {wind_speed}m/s \nمیزان ابر: %{cloud_all} \nمیزان دید: {visibility} متر\n\n{time}\n@ir_{x}_weather"
        )
        return message
    else:
        logging.error(
            f"خطا در دریافت اطلاعات آب و هوا: {response.status_code} - {response.text}"
        )
        return "خطا در دریافت اطلاعات آب و هوا."

async def send_weather(city_id, channel_id):
    message = get_weather(city_id)
    bot = telegram.Bot(token="7199265167:AAHRWNMZzvQaDTcHiee6lAjuqBTiQL2DIgk")  # توکن ربات تلگرام خود را وارد کنید
    try:
        await bot.send_message(chat_id=channel_id, text=message)
        logging.info(f"Your Message Sent To Channel {channel_id}")
    except Exception as e:
        logging.error(f"Unexpected Error On send_weather: {e}")

def main():
    scheduler = AsyncIOScheduler()
    scheduler2 = AsyncIOScheduler()
    scheduler3 = AsyncIOScheduler()
    # ارسال آب و هوای تهران به کانال مربوطه
    scheduler.add_job(send_weather, "interval", seconds=3600, args=[TEHRAN_CITY_ID, TEHRAN_CHANNEL_ID])
    # ارسال آب و هوای قم به کانال مربوطه
    scheduler2.add_job(send_weather, "interval", seconds=3600, args=[QOM_CITY_ID, QOM_CHANNEL_ID])

    scheduler3.add_job(send_weather, "interval", seconds=3600, args=[MASHHAD_CITY_ID, MASHHAD_CHANNEL_ID])

    scheduler.start()
    scheduler2.start()
    scheduler3.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()