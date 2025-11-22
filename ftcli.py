import typer

from commands.stats import Stats
from commands.approve import Approve
from commands.create import CreateTeam
from commands.join import JoinTeam
from commands.pending import Pending

App = typer.Typer()

App.add_typer(Stats().App, name="stats")
App.add_typer(Pending().App, name="pending")
App.add_typer(JoinTeam().App, name="join-team")
App.add_typer(Approve().App, name="approve")
App.add_typer(CreateTeam().App, name="create-team")
        

if __name__ == "__main__":
    App()