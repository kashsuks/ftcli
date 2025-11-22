import typer
import asyncio
from db import init

class Init:
    def __init__(self):
        self.App = typer.Typer()
        
        @self.App.command()
        def database():
            asyncio.run(init())