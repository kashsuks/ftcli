import typer
import asyncio
from db import getDB

class JoinTeam:
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def request(teamNumber: int, username: str, passcode: str):
            asyncio.run(self._request(teamNumber, username, passcode))
    
    async def _request(self, teamNumber: int, username: str, passcode: str):
        conn = await getDB()
        
        team = await conn.fetchrow(
            "SELECT passcode FROM teams WHERE team_number=$1", teamNumber
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
        """, teamNumber, username)
        
        print("Join request submitted")
        await conn.close()