from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.cli import make_cli

import commands.create_team
import commands.join_team

class FTCLI(App):
    CSS_PATH = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
cli = make_cli(FTCLI)

if __name__ == "__main__":
    cli()