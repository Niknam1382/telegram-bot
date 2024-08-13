import requests
import logging
import asyncio
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

CHANNEL_ID = "@midonish"

def get_danesh():
    session = requests.session()
    url = "https://one-api.ir/danestani/?token=280176:66b6abf8123ee"
    response = session.get(url)
    data = response.json()

    if response.status_code == 200:
        d = data['result']['Content']

        message = (
            f"{d}\n\n⁉️ @midonish"
        )
        return message
    else:
        logging.error(
            f"خطا در دریافت اطلاعات آب و هوا: {response.status_code} - {response.text}"
        )
        return "خطا در دریافت اطلاعات آب و هوا."

# تابع برای ارسال پیام به کانال تلگرام
async def send_weather():
    message = get_danesh()
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