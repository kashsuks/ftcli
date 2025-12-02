import typer
import asyncio
from db import getDB
from auth import getUser
from utils.ftcScout import getTeam

class Stats:
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def show(username: str):
            """
            Used to start and get user and data

            Args:
                username (str): The username of the user (if exists)
            """
            username = getUser()
            if not username:
                print("You must be logged in!")
                return
            
            asyncio.run(self._show(username))
    
    async def _show(self, username: str):
        """
        Private to fetch data not to be used anywhere else
        """
        conn = await getDB()
        team = await conn.fetchrow("""
            SELECT t.team_number, t.team_name, t.location, t.website
            FROM teams t
            JOIN team_members m ON t.team_number = m.team_number
            WHERE m.username=$1
        """, username)
        
        if not team:
            print("You are not in a team.")
            await conn.close()
            return
    
        remote = await getTeam(team["team_number"])
        
        print("\n=== Team Info ===")
        print(f"Team number: {team['team_number']}")
        print(f"Team name: {team['team_name']}")
        print(f"Location: {team['location']}")
        print(f"Website {team['website']}")
        print("\n=== FTCScout Data ===")
        print(remote)
        
        await conn.close()