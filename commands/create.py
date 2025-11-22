import typer
import asyncio
from db import getDB

class CreateTeam:
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def new(
            *,
            teamNumber: int,
            teamName: str, 
            location: str, 
            website: str, 
            passcode: str
        ):
            asyncio.run(
                self._new(teamNumber, teamName, location, website, passcode)
            )

    async def _new(self, teamNumber, teamName, location, website, passcode):
        conn = await getDB()
        
        await conn.execute("""
            INSERT INTO teams (team_number, team_name, location, website, passcode)
            VALUES ($1, $2, $3, $4, $5)
        """, teamNumber, teamName, location, website, passcode)
        
        print("Team created")
        await conn.close()