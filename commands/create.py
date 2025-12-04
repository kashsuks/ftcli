import typer
import asyncio

from database import get_database_connection
from auth import get_user

class CreateTeam:
    """
    Input information for team into database form TUI
    """
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def new(
            *,
            team_number: int = typer.Option(None, prompt="Team Number"),
            team_name: str = typer.Option(None, prompt="Team Name"), 
            location: str = typer.Option(None, prompt="Location"), 
            website: str = typer.Option(None, prompt="Website"), 
            passcode: str = typer.Option(None, prompt="Team Passcode", hide_input=True)
        ):
            
            creator = get_user()
            if not creator:
                print("You must be logged in to create a team")
                return
            
            asyncio.run(
                self._new(team_number, team_name, location, website, passcode, creator)
            )

    async def _new(self, team_number, team_name, location, website, passcode, creator):
        conn = await get_database_connection()
        
        try:
            await conn.execute("""
                INSERT INTO teams (team_number, team_name, location, website, passcode, creator)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, team_number, team_name, location, website, passcode, creator)
            
            await conn.execute("""
                INSERT INTO team_members (team_number, username)
                VALUES ($1,$2)
            """, team_number, creator)
            
            print("Team created successfully!")
        except Exception as e:
            print(f"Error creating team: {e}")
        finally:
            await conn.close()
