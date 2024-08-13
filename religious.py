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
    iran_time_str = iran_jdate.strftime('%Y/%m/%d - %A')
    iran_time_str = iran_time_str.replace('Saturday', 'شنبه')
    iran_time_str = iran_time_str.replace('Sunday', 'یک‌شنبه')
    iran_time_str = iran_time_str.replace('Monday', 'دوشنبه')
    iran_time_str = iran_time_str.replace('Tuesday', 'سه‌شنبه')
    iran_time_str = iran_time_str.replace('Wednesday', 'چهارشنبه')
    iran_time_str = iran_time_str.replace('Thursday', 'پنج‌شنبه')
    iran_time_str = iran_time_str.replace('Friday', 'جمعه')
    return '⏱️ ' + iran_time_str

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CHANNEL_ID = "@tehran_religius_times"

def get_religios():
    session = requests.session()
    url = 'https://one-api.ir/owghat/?token=280176:66b6abf8123ee&city=%D8%AA%D9%87%D8%B1%D8%A7%D9%86&en_num=true'
    response = session.get(url)
    data = response.json()

    if response.status_code == 200:
        city = data['result']['city']
        azan_sobh = data['result']['azan_sobh']
        toloe_aftab = data['result']['toloe_aftab']
        azan_zohre = data['result']['azan_zohre']
        ghorob_aftab = data['result']['ghorob_aftab']
        azan_maghreb = data['result']['azan_maghreb']
        nime_shabe_sharie = data['result']['nime_shabe_sharie']
        month = data['result']['month']
        day = data['result']['day']
        longitude = data['result']['longitude']
        latitude = data['result']['latitude']
                
        message = (
            f"🕌 اوقات شرعی شهر تهران\n\nاذان صبح : {azan_sobh}\nطلوع آفتاب : {toloe_aftab}\nاذان ظهر : {azan_zohre}\nغروب آفتاب : {ghorob_aftab}\nاذان مغرب : {azan_maghreb}\nنیمه شب شرعی : {nime_shabe_sharie}\n\n{get_iran_time()}\n🌍 @tehran_religius_times"
        )
        return message
    else:
        logging.error(
            f"خطا در دریافت اطلاعات آب و هوا: {response.status_code} - {response.text}"
        )
        return "خطا در دریافت اطلاعات آب و هوا."

# تابع برای ارسال پیام به کانال تلگرام
async def send_weather():
    message = get_religios()
    bot = telegram.Bot(token="7199265167:AAHRWNMZzvQaDTcHiee6lAjuqBTiQL2DIgk")
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        logging.info("Your Message Send To Channel")
    except Exception as e:
        logging.error(f"Unxpected Error On Send_weather: {e}")

def main():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_weather, "interval", seconds=43200)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()