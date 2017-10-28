import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get('https://api.github.com/events') as resp:
        print(resp.status)
        print(await resp.text())
