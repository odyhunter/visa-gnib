import time
import urllib.request
import asyncio
import aiohttp
import config
import async_timeout
from config import HEADERS, TYPE_VISA


def make_header(header, appointment_type):
    if appointment_type == 'gnib':
        header['host'] = config.GNIB_HOST
        return header
    elif appointment_type == 'visa':
        header['host'] = config.VISA_HOST
        return header


async def fetch(session, url):
    with async_timeout.timeout(10):
        # empty headers needs for the response server to answer
        async with session.get(url, headers=make_header(HEADERS, TYPE_VISA)) as response:
            return await response
