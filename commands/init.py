import typer
import asyncio
from database import init

class Init:
    def __init__(self):
        self.App = typer.Typer()
        
        @self.App.command()
        def database():
            asyncio.run(init())
