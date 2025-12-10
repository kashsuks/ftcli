import typer
import sys

from ftcli.commands.stats import Stats
from ftcli.commands.approve import Approve
from ftcli.commands.create import CreateTeam
from ftcli.commands.join import JoinTeam
from ftcli.commands.pending import Pending
from ftcli.commands.init import Init
from ftcli.commands.auth import Auth

App = typer.Typer()

App.add_typer(Init().App, name="init")
App.add_typer(Auth().App, name="auth")
App.add_typer(Stats().App, name="stats")
App.add_typer(Pending().App, name="pending")
App.add_typer(JoinTeam().App, name="join-team")
App.add_typer(Approve().App, name="approve")
App.add_typer(CreateTeam().App, name="create-team")

@App.command()
def configure():
    """
    Configure FTC CLI database connection
    """
    from ftcli.utils.config import setup_config
    setup_config()

def main():
    """
    Main entry point for the CLI
    """
    from pathlib import Path
    import os
    
    home_config = Path.home() / ".ftcli" / "config.env"
    
    if not home_config.exists() and not os.getenv("POSTGRES_URL"):
        if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in ['configure', '--help', '-h']):
            print("\nFirst time setup required!")
            print("Run: ftcli configure\n")
            return
    
    if len(sys.argv) == 1:
        from ftcli.tui import MainApp
        app = MainApp()
        app.run()
    else:
        App()

if __name__ == "__main__":
    main()