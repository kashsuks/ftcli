import typer
import asyncio
from db import getDB

class Pending:
    def __init__(self):
        self.App = typer.Typer()
        
        @self.App.command()
        def list(teamNumber: int):
            asyncio.run(self._list(teamNumber))
            
    async def _list(self, teamNumber: int):
        conn = await getDB()
        
        rows = await conn.fetch("""
            SELECT id, username
            FROM join_requests
            WHERE team_number=$1 AND status='pending'
        """, teamNumber)
        
        for r in rows:
            print(f"{r['id']}: {r['username']}")
            
        await conn.close()