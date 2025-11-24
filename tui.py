from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, Label, Input
from textual.screen import Screen
from textual import on
import asyncio
import webbrowser
from auth import getUser, authenticate, setUser, clear
from db import getDB

class LoginScreen(Screen):
    """Login screen"""
    
    CSS = """
    LoginScreen {
        align: center middle;
    }
    
    #login_container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2;
        background: $surface;
    }
    
    Input {
        margin: 1 0;
    }
    
    Button {
        width: 100%;
        margin: 1 0;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }
    
    .error {
        color: $error;
        text-align: center;
        margin: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(id="login_container"):
            yield Label("FTC CLI", classes="title")
            yield Label("Please login to continue", classes="title")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            yield Button("Login", variant="primary", id="login_btn")
            yield Label("", id="error_msg", classes="error")
    
    @on(Button.Pressed, "#login_btn")
    async def login(self):
        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        error = self.query_one("#error_msg", Label)
        
        username = username_input.value
        password = password_input.value
        
        if not username or not password:
            error.update("Please enter username and password")
            return
        
        if await authenticate(username, password):
            setUser(username)
            self.app.username = username
            await self.app.load_data()
            self.app.pop_screen()
        else:
            error.update("Invalid username or password")
            password_input.value = ""

class CreateTeamScreen(Screen):
    """Create team screen"""
    
    CSS = """
    CreateTeamScreen {
        align: center middle;
    }
    
    #create_container {
        width: 70;
        height: auto;
        border: solid $primary;
        padding: 2;
        background: $surface;
    }
    
    Input {
        margin: 1 0;
    }
    
    Button {
        margin: 1 0;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }
    
    .error {
        color: $error;
        text-align: center;
        margin: 1 0;
    }
    
    .success {
        color: $success;
        text-align: center;
        margin: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(id="create_container"):
            yield Label("Create New Team", classes="title")
            yield Input(placeholder="Team Number", id="team_number")
            yield Input(placeholder="Team Name", id="team_name")
            yield Input(placeholder="Location", id="location")
            yield Input(placeholder="Website", id="website")
            yield Input(placeholder="Team Passcode", password=True, id="passcode")
            yield Label("", id="msg", classes="error")
            with Horizontal():
                yield Button("Create", variant="primary", id="create_btn")
                yield Button("Cancel", variant="default", id="cancel_btn")
    
    @on(Button.Pressed, "#create_btn")
    async def create(self):
        team_number = self.query_one("#team_number", Input).value
        team_name = self.query_one("#team_name", Input).value
        location = self.query_one("#location", Input).value
        website = self.query_one("#website", Input).value
        passcode = self.query_one("#passcode", Input).value
        msg = self.query_one("#msg", Label)
        
        if not all([team_number, team_name, location, website, passcode]):
            msg.update("All fields are required!")
            msg.styles.color = "red"
            return
        
        try:
            team_number = int(team_number)
        except ValueError:
            msg.update("Team number must be a number!")
            msg.styles.color = "red"
            return
        
        creator = getUser()
        conn = await getDB()
        
        try:
            await conn.execute("""
                INSERT INTO teams (team_number, team_name, location, website, passcode, creator)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, team_number, team_name, location, website, passcode, creator)
            
            await conn.execute("""
                INSERT INTO team_members (team_number, username)
                VALUES ($1, $2)
            """, team_number, creator)
            
            msg.update("Team created successfully!")
            msg.styles.color = "green"
            await asyncio.sleep(1)
            await self.app.load_data()
            self.app.pop_screen()
        except Exception as e:
            msg.update(f"Error: {str(e)}")
            msg.styles.color = "red"
        finally:
            await conn.close()
    
    @on(Button.Pressed, "#cancel_btn")
    def cancel(self):
        self.app.pop_screen()

class JoinTeamScreen(Screen):
    """Join team screen"""
    
    CSS = """
    JoinTeamScreen {
        align: center middle;
    }
    
    #join_container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2;
        background: $surface;
    }
    
    Input {
        margin: 1 0;
    }
    
    Button {
        margin: 1 0;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }
    
    .error {
        color: $error;
        text-align: center;
        margin: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(id="join_container"):
            yield Label("Join Team", classes="title")
            yield Input(placeholder="Team Number", id="team_number")
            yield Input(placeholder="Team Passcode", password=True, id="passcode")
            yield Label("", id="msg", classes="error")
            with Horizontal():
                yield Button("Request to Join", variant="primary", id="join_btn")
                yield Button("Cancel", variant="default", id="cancel_btn")
    
    @on(Button.Pressed, "#join_btn")
    async def join(self):
        team_number = self.query_one("#team_number", Input).value
        passcode = self.query_one("#passcode", Input).value
        msg = self.query_one("#msg", Label)
        
        if not team_number or not passcode:
            msg.update("All fields are required!")
            msg.styles.color = "red"
            return
        
        try:
            team_number = int(team_number)
        except ValueError:
            msg.update("Team number must be a number!")
            msg.styles.color = "red"
            return
        
        username = getUser()
        conn = await getDB()
        
        try:
            team = await conn.fetchrow(
                "SELECT passcode FROM teams WHERE team_number=$1", team_number
            )
            
            if not team:
                msg.update("Team does not exist!")
                msg.styles.color = "red"
                return
            
            if team["passcode"] != passcode:
                msg.update("Incorrect passcode!")
                msg.styles.color = "red"
                return
            
            await conn.execute("""
                INSERT INTO join_requests (team_number, username)
                VALUES ($1, $2)
            """, team_number, username)
            
            msg.update("Join request submitted!")
            msg.styles.color = "green"
            await asyncio.sleep(1)
            self.app.pop_screen()
        except Exception as e:
            msg.update(f"Error: {str(e)}")
            msg.styles.color = "red"
        finally:
            await conn.close()
    
    @on(Button.Pressed, "#cancel_btn")
    def cancel(self):
        self.app.pop_screen()

class ViewTeamScreen(Screen):
    """View team details screen"""
    
    CSS = """
    ViewTeamScreen {
        align: center middle;
    }
    
    #view_container {
        width: 70;
        height: auto;
        border: solid $primary;
        padding: 2;
        background: $surface;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }
    
    .info {
        margin: 1 0;
    }
    
    .label {
        text-style: bold;
        color: $accent;
    }
    
    Button {
        width: 30;
        margin: 1 0;
    }
    """
    
    def __init__(self, team_data):
        """Initialize
        
        Args:
            team_data: Team data
        """
        super().__init__()
        self.team_data = team_data
    
    def compose(self) -> ComposeResult:
        with Container(id="view_container"):
            yield Label("Team Information", classes="title")
            yield Label(f"[bold cyan]Team Number:[/] {self.team_data['team_number']}", classes="info")
            yield Label(f"[bold cyan]Team Name:[/] {self.team_data['team_name']}", classes="info")
            yield Label(f"[bold cyan]Location:[/] {self.team_data['location']}", classes="info")
            yield Label(f"[bold cyan]Website:[/] {self.team_data['website']}", classes="info")
            with Horizontal():
                yield Button("Open Website", variant="primary", id="open_web")
                yield Button("Close", variant="default", id="close_btn")
    
    @on(Button.Pressed, "#open_web")
    def open_website(self):
        """Opens the website"""
        webbrowser.open(self.team_data['website'])
    
    @on(Button.Pressed, "#close_btn")
    def close(self):
        """Closes the screen"""
        self.app.pop_screen()

class MainApp(App):
    """Main application"""
    
    CSS = """
    Screen {
        background: $background;
    }
    
    #welcome {
        width: 100%;
        height: auto;
        text-align: center;
        padding: 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    #updates {
        width: 100%;
        height: auto;
        padding: 1;
        border: solid $accent;
        margin: 1 0;
        background: $surface;
    }
    
    #menu_container {
        width: 60;
        height: auto;
        align: center middle;
    }
    
    Button {
        width: 100%;
        margin: 1 0;
    }
    
    .update-item {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("l", "logout", "Logout"),
    ]
    
    def __init__(self):
        """Initialize"""
        super().__init__()
        self.username = None
        self.team_data = None
        self.is_owner = False
        self.pending_requests = []
    
    def on_mount(self) -> None:
        """Called when app is mounted"""
        self.username = getUser()
        if not self.username:
            self.push_screen(LoginScreen())
        else:
            asyncio.create_task(self.load_data())
    
    async def load_data(self):
        """Load the team's data via postgres"""
        conn = await getDB()
        
        team = await conn.fetchrow("""
            SELECT t.team_number, t.team_name, t.location, t.website, t.creator
            FROM teams t
            JOIN team_members m ON t.team_number = m.team_number
            WHERE m.username=$1
        """, self.username)
        
        if team:
            self.team_data = dict(team)
            self.is_owner = team['creator'] == self.username
            
            # Get pending requests if the user is the owner
            if self.is_owner:
                requests = await conn.fetch("""
                    SELECT id, username, created_at
                    FROM join_requests
                    WHERE team_number=$1 AND status='pending'
                    ORDER BY created_at DESC
                """, team['team_number'])
                self.pending_requests = [dict(r) for r in requests]
        
        await conn.close()
        self.update_ui()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="welcome")
        yield Static(id="updates")
        with Vertical(id="menu_container"):
            if not self.team_data:
                yield Button("Join Team", id="join_team", variant="primary")
                yield Button("Create Team", id="create_team", variant="success")
            else:
                yield Button("View Team", id="view_team", variant="primary")
                yield Button("Leave Team", id="leave_team", variant="error")
            yield Button("Settings", id="settings", variant="default")
            yield Button("More", id="more", variant="default")
        yield Footer()
    
    def update_ui(self):
        """Update UI elements"""
        try:
            # Welcome message
            welcome = self.query_one("#welcome", Static)
            role = " (Team Owner)" if self.is_owner else ""
            welcome.update(f"Welcome, {self.username}{role}!")
            
            # Update notifications
            updates = self.query_one("#updates", Static)
            if self.is_owner and self.pending_requests:
                content = f"[bold yellow]📢 Updates:[/]\n"
                content += f"• {len(self.pending_requests)} pending join request(s)\n"
                for req in self.pending_requests[:3]:
                    content += f"  - {req['username']} requested to join\n"
                updates.update(content)
            else:
                updates.update("")
        except Exception:
            pass  # Widgets not ready yet
    
    @on(Button.Pressed, "#join_team")
    async def handle_join_team(self):
        """Handles joining a team"""
        self.push_screen(JoinTeamScreen())
    
    @on(Button.Pressed, "#create_team")
    async def handle_create_team(self):
        """Handles creating a team"""
        self.push_screen(CreateTeamScreen())
    
    @on(Button.Pressed, "#view_team")
    async def handle_view_team(self):
        """Handles viewing a team and its data"""
        if self.team_data:
            self.push_screen(ViewTeamScreen(self.team_data))
    
    @on(Button.Pressed, "#leave_team")
    async def handle_leave_team(self):
        """Handles leaving a team"""
        if not self.team_data:
            return
        
        conn = await getDB()
        try:
            await conn.execute("""
                DELETE FROM team_members
                WHERE team_number=$1 AND username=$2
            """, self.team_data['team_number'], self.username)
            
            self.team_data = None
            self.is_owner = False
            self.pending_requests = []
            await self.load_data()
            self.notify("Left team successfully! Please restart.")
            self.exit()
        finally:
            await conn.close()
    
    @on(Button.Pressed, "#settings")
    def handle_settings(self):
        """Handle settings"""
        self.notify("Settings - Coming soon!")
    
    @on(Button.Pressed, "#more")
    def handle_more(self):
        """Handle more options"""
        self.notify("More options - Coming soon!")
    
    def action_logout(self):
        """Logout of the current session"""
        clear()
        self.exit()
    
    def action_quit(self):
        """Quit the application"""
        self.exit()

if __name__ == "__main__":
    app = MainApp()
    app.run()