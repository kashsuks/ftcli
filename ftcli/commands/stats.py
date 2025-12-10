import typer
import asyncio
from ftcli.database import get_database_connection
from ftcli.auth import get_user
from ftcli.utils.ftc_scout import get_team

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
            username = get_user()
            if not username:
                print("You must be logged in!")
                return
            
            asyncio.run(self._show(username))
    
    async def _show(self, username: str):
        """
        Private to fetch data not to be used anywhere else
        """
        conn = await get_database_connection()
        team_data = await conn.fetchrow("""
            SELECT t.team_number, t.team_name, t.location, t.website
            FROM teams t
            JOIN team_members m ON t.team_number = m.team_number
            WHERE m.username=$1
        """, username)
        
        if not team_data:
            print("You are not in a team.")
            await conn.close()
            return
    
        remote = await get_team(team_data["team_number"])
        
        print("\n=== Team Info ===")
        print(f"Team number: {team_data['team_number']}")
        print(f"Team name: {team_data['team_name']}")
        print(f"Location: {team_data['location']}")
        print(f"Website {team_data['website']}")
        print("\n=== FTCScout Data ===")
        print(remote)
        
        await conn.close()
