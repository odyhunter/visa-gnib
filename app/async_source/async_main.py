import json
import aiohttp
import asyncio
from datetime import (
    datetime,
    timedelta,
    time
)
from config import (
    TYPE_VISA,
    DAYS_UPDATE_RANGE,
    TODAY_plus_2,
    VISA_UPDATE_URL,
    GNIB_UPDATE_URL
)
from utils import fetch


async def fetch_appointment(index, appointment_type):
    date_obj = datetime.combine(TODAY_plus_2 + timedelta(days=index), time())
    print(f'Fetching appointments for {appointment_type} {str(date_obj)}')
    # [Parameters for request]
    # make 1 liner
    day = str(date_obj)[8:10]
    month = str(date_obj)[5:7]
    year = str(date_obj)[0:4]
    url = GNIB_UPDATE_URL if appointment_type == 'gnib' else VISA_UPDATE_URL
    url = url.format(day, month, year)
    # make request
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url)
        response_json = response.json()
        print(response_json)


async def update_visa():
    tasks = [asyncio.ensure_future(
        fetch_appointment(i, TYPE_VISA)) for i in range(DAYS_UPDATE_RANGE)]
    await asyncio.wait(tasks)
    print(f'Done! Checked {DAYS_UPDATE_RANGE} {TYPE_VISA} Daays :)')


ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(update_visa())
ioloop.close()