from textual.cli import command
from db import getDB

@command("approve")
async def approve(requestId: int, approve: bool):
    conn = await getDB()
    
    request = await conn.fetchrow("SELECT * FROM join_requests WHERE id=$1", requestId)
    if not request:
        print("Request not found")
        return
    
    if approve:
        await conn.execute("""
            INSERT INTO team_members (team_number, username)
            VALUES ($1,$2))
        """, request["team_number"], request["username"])
        
        await conn.execute("""
            UPDATE join_requests SET status='approved' WHERE id=$1
        """, requestId)
        print("Approved.")
    else:
        await conn.execute("""
            UPDATE join_requests SET status='rejected' WHERE id=$1
        """, requestId)
    
    await conn.close()