import typer
import asyncio

from database import get_database_connection
from auth import get_user

class JoinTeam:
    def __init__(self):
        self.App = typer.Typer()
        
        @self.App.command()
        def request(
            team_number: int = typer.Option(None, prompt="Team Number"), 
            passcode: str = typer.Option(None, prompt="Team passcode")
        ):
            username = get_user()
            if not username:
                print("You must be logged in to join a team!")
                return
            
            asyncio.run(self._request(team_number, username, passcode))
    
    async def _request(self, team_number: int, username: str, passcode: str):
        conn = await get_database_connection()
        
        team = await conn.fetchrow(
            "SELECT passcode FROM teams WHERE team_number=$1", team_number
        )
        
        if not team:
            print("Team does not exist")
            await conn.close()
            return
        
        if team["passcode"] != passcode:
            print("Incorrect passcode")
            await conn.close()
            return
        
        await conn.execute("""
            INSERT INTO join_requests (team_number, username)
            VALUES ($1, $2)
        """, team_number, username)
        
        print("Join request submitted")
        await conn.close()
