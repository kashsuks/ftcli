import typer
import asyncio
from database import get_database_connection

class Pending:
    """
    
    """
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def list(team_number: int):
            """
            Lists data about the team and number
            Args:
                teamNumber (int): team number that the user is under
            """
            asyncio.run(self._list(team_number))            
    async def _list(self, team_number: int):
        """
        Private to list the data of the user team number and status
        """
        conn = await get_database_connection()
        rows = await conn.fetch("""
            SELECT id, username
            FROM join_requests
            WHERE team_number=$1 AND status='pending'
        """, team_number)
        for r in rows:
            print(f"{r['id']}: {r['username']}")
        await conn.close()
