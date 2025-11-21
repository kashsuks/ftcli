import asyncpg
from config import DB_URL

async def getDB():
    """
    Connects to the PostgreSQL Database

    Returns:
        _type_: _description_
    """
    return await asyncpg.connect(DB_URL)

async def init():
    conn = await getDB()
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        team_number INT PRIMARY KEY,
        team_name TEXT NOT NULL,
        location TEXT,
        website TEXT,
        passcode TEXT NOT NULL,
        creator TEXT NOT NULL
    );
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS team_members (
        id SERIAL PRIMARY KEY,
        team_number INT REFERENCES teams(team_number),
        username TEXT NOT NULL,
        status TEXT DEFAULT 'pending'
    );
    """)
    await conn.close()