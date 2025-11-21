import aiohttp

BASE = "https://api.ftcscout.org/rest/v1"

async def getTeam(number: int):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{BASE}/teams/{number}") as r:
            if r.status != 200:
                return None
            return await r.json()