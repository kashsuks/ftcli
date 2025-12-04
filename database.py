import asyncpg # pylint: disable=import-error
from utils.config import DB_URL

async def get_database_connection():
    """
    Connects to the PostgreSQL Database

    Returns:
        Connection: asyncpg connection object
    """
    return await asyncpg.connect(DB_URL)

async def init() -> None:
    """
    Initializes the database and sets up all of the tables needed in order to store all data
    """
    conn = await get_database_connection()
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        team_number INT PRIMARY KEY,
        team_name TEXT NOT NULL,
        location TEXT,
        website TEXT,
        passcode TEXT NOT NULL,
        creator TEXT REFERENCES users(username)
    );
    """)
    
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS team_members (
        id SERIAL PRIMARY KEY,
        team_number INT REFERENCES teams(team_number),
        username TEXT NOT NULL,
        UNIQUE(team_number, username)
    );
    """)
    
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS join_requests (
        id SERIAL PRIMARY KEY,
        team_number INT REFERENCES teams(team_number),
        username TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    print("Database initialized successfully")
    await conn.close()
