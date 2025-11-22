import typer

from auth import getUser

from commands.stats import Stats
from commands.approve import Approve
from commands.create import CreateTeam
from commands.join import JoinTeam
from commands.pending import Pending
from commands.init import Init
from commands.auth import Auth

App = typer.Typer()

def checkAuth():
    """
    Check if the user is logged in before running commands
    """
    user = getUser()
    if not user:
        print("You must be logged in to use this command!")
        print("Run 'ftcli.py auth register' to create an account")
        print("Run 'ftcli.py auth login' to login")

App.add_typer(Init().App, name="init")
App.add_typer(Auth().App, name="auth")
App.add_typer(Stats().App, name="stats")
App.add_typer(Pending().App, name="pending")
App.add_typer(JoinTeam().App, name="join-team")
App.add_typer(Approve().App, name="approve")
App.add_typer(CreateTeam().App, name="create-team")
        

if __name__ == "__main__":
    App()