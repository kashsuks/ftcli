import typer
import asyncio
from db import getDB

class Approve:
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def request(requestId: int, allowed: bool):
            asyncio.run(self._request(requestId, allowed))
            
    async def _request(self, requestId: int, allowed: bool):
        conn = await getDB()
        
        req = await conn.fetchrow(
            "SELECT * FROM join_requests WHERE id=$1", requestId
        )
        
        if not req:
            print("Request not found")
            await conn.close()
            return
        
        if allowed:
            await conn.execute("""
                INSERT INTO team_members (team_member, username)
                VALUES ($1, $2)
            """, req["team_number"], req["username"])
            
            await conn.execute("""
                UPDATE join_requests SET status='approved' WHERE id=$1
            """, requestId)
            
            print("Approved")
        else:
            await conn.execute("""
                UPDATE join_requests SET status='rejected' WHERE id=$1
            """, requestId)
        
        await conn.close()