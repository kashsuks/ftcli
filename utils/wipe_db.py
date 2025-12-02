import asyncio
import asyncpg
from config import DB_URL

async def wipe():
    """
    Used to drop all of the database
    """
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("DROP TABLE IF EXISTS join_requests CASCADE;")
    await conn.execute("DROP TABLE IF EXISTS team_members CASCADE;")
    await conn.execute("DROP TABLE IF EXISTS teams CASCADE;")
    await conn.close()
    print("Database wiped")
asyncio.run(wipe())
