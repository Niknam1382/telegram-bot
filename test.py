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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CHANNEL_ID = "@ir_tehran_weather"
WEATHER_API_KEY = "c98eb50389c22cd88756d85efb8b4df1"
CITY_ID = "112931"


def get_weather():
    session = requests.session()
    url = f"http://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    response = session.get(url)
    data = response.json()

    if response.status_code == 200:
        city = data['name']
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        cloud_all = data['clouds']['all']
        visibility = data['visibility']

        if city == 'تهران':
            x = 'tehran'
        message = (
            f"آب و هوای {city}:\n\nوضعیت: {weather}\nدما: {temp} درجه سانتیگراد\nرطوبت: %{humidity}\nسرعت وزش باد: {wind_speed}m/s \nمیزان ابر: %{cloud_all} \nمیدان دید: {visibility} متر\n\n{get_iran_time()}\n🌥️ @ir_{x}_weather"
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

    scheduler.add_job(send_weather, "interval", seconds=3600)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()