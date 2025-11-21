from textual.cli import command
from db import getDB

@command("pending")
async def pending(teamNumber: int):
    conn = await getDB()
    rows = await conn.fetch("""
        SELECT id, username FROM join_requests
        WHERE team_number=$1 AND status='pending'
    """, teamNumber)
    
    for r in rows:
        print(f"{r['id']}: {r['username']}")
        
    await conn.close()