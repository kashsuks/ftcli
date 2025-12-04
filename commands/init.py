import typer
import asyncio
from database import init

class Init:
    """
    Initialize commands and get ready for database setup
    """
    def __init__(self):
        self.App = typer.Typer()
        
        @self.App.command()
        def database():
            asyncio.run(init())
