import asyncio
import webbrowser

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, Label, Input
from textual.screen import Screen, ModalScreen
from textual import on

from auth import get_user, authenticate, set_user, clear
from database import get_database_connection

class ConfirmKickScreen(ModalScreen):
    """
    Confirmation dialog for kicking a member
    """
    
    CSS = """
    ConfirmKickScreen {
        align: center middle;
    }
    
    #confirm_container {
        width: 50;
        height: auto;
        border: solid $error;
        padding: 2;
        background: $surface;
    }

    .title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin: 1 0;
    }
    
    .message {
        text-align: center;
        margin: 1 0;
    }
    
    Button {
        width: 50%;
        margin: 1;
    }
    """
    
    def __init__(self, username: str, team_number: int):
        super().__init__()
        self.username = username
        self.team_number = team_number
    def compose(self) -> ComposeResult:
        with Container(id="confirm_container"):
            yield Label("Confirm Kick", classes="title")
            yield Label(f"Are you sure you want to kick {self.username} from the team?", classes="message")
            with Horizontal():
                yield Button("Confirm", variant="error", id="confirm_btn")
                yield Button("Cancel", variant="default", id="cancel_btn")
    @on(Button.Pressed, "#confirm_btn")
    async def confirm_kick(self):
        """
        Removes user from the databse if authorized to get kicked
        
        :param self: Self that can use class attributes
        """
        conn = await get_database_connection()
        try:
            await conn.execute("""
                DELETE FROM team_members
                WHERE team_number=$1 AND username=$2
            """, self.team_number, self.username)
            self.dismiss(True)
        except Exception as e:
            self.app.notify(f"Error: {str(e)}")
            self.dismiss(False)
        finally:
            await conn.close()
    @on(Button.Pressed, "#cancel_btn")
    def cancel(self):
        self.dismiss(False)

class LoginScreen(Screen):
    """
    Login screen
    """
    
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
        """
        Logic screen that asks for the username and password
        """
        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        error = self.query_one("#error_msg", Label)
        username = username_input.value
        password = password_input.value
        
        if not username or not password:
            error.update("Please enter username and password")
            return
        
        if await authenticate(username, password):
            set_user(username)
            self.app.username = username
            await self.app.load_data()
            self.app.pop_screen()
        else:
            error.update("Invalid username or password!")
            password_input.value = ""

class CreateTeamScreen(Screen):
    """
    Create team screen
    """
    
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
        """
        Compose method for setting up variables needed

        Returns:
            ComposeResult: Iterable widget

        Yields:
            Iterator[ComposeResult]
        """
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
        """
        Creates all parameters and the screen for creating a team
        
        :param self: Allows the usage of class attributes
        """
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
        creator = get_user()
        conn = await get_database_connection()
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
        
        username = get_user()
        conn = await get_database_connection()
        
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
        width: 80;
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
    
    .section-title {
        text-style: bold;
        color: $accent;
        margin: 2 0 1 0;
    }
    
    .info {
        margin: 1 0;
    }
    
    .label {
        text-style: bold;
        color: $accent;
    }
    
    .member-card {
        border: solid $primary;
        padding: 1;
        margin: 1 0;
        background: $panel;
    }
    
    .request-card {
        border: solid $warning;
        padding: 1;
        margin: 1 0;
        background: $panel;
    }
    
    Button {
        margin: 1;
    }
    
    .action-buttons {
        width: auto;
    }
    
    .request-info {
        width: 1fr;
    }
    """
    
    def __init__(self, team_data, members, pending_requests):
        super().__init__()
        self.team_data = team_data
        self.members = members
        self.pending_requests = pending_requests
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="view_container"):
            yield Label("Team Information", classes="title")
            yield Label(f"[bold cyan]Team Number:[/] {self.team_data['team_number']}", classes="info")
            yield Label(f"[bold cyan]Team Name:[/] {self.team_data['team_name']}", classes="info")
            yield Label(f"[bold cyan]Location:[/] {self.team_data['location']}", classes="info")
            yield Label(f"[bold cyan]Website:[/] {self.team_data['website']}", classes="info")
            
            yield Label("Team Members", classes="section-title")
            for member in self.members:
                role = "Creator" if member['username'] == self.team_data['creator'] else "Member"
                with Container(classes="member-card"):
                    yield Label(f"👤 {member['username']} - {role}")
            
            if self.pending_requests:
                yield Label("Pending Join Requests", classes="section-title")
                for req in self.pending_requests:
                    with Horizontal(classes="request-card"):
                        yield Label(f"📨 {req['username']} requested to join", classes="request-info")
                        with Horizontal(classes="action-buttons"):
                            yield Button("✓", variant="success", id=f"approve_{req['id']}")
                            yield Button("✗", variant="error", id=f"reject_{req['id']}")
            
            with Horizontal():
                yield Button("Open Website", variant="primary", id="open_web")
                yield Button("Close", variant="default", id="close_btn")
    
    @on(Button.Pressed)
    async def handle_button(self, event: Button.Pressed):
        button_id = event.button.id
        
        if button_id == "open_web":
            webbrowser.open(self.team_data['website'])
        elif button_id == "close_btn":
            self.app.pop_screen()
        elif button_id.startswith("approve_"):
            request_id = int(button_id.split("_")[1])
            await self.handle_request(request_id, True)
        elif button_id.startswith("reject_"):
            request_id = int(button_id.split("_")[1])
            await self.handle_request(request_id, False)
    
    async def handle_request(self, request_id: int, approved: bool):
        conn = await get_database_connection()
        try:
            req = await conn.fetchrow(
                "SELECT * FROM join_requests WHERE id=$1", request_id
            )
            
            if not req:
                self.app.notify("Request not found")
                return
            
            if approved:
                await conn.execute("""
                    INSERT INTO team_members (team_number, username)
                    VALUES ($1, $2)
                """, req["team_number"], req["username"])
                
                await conn.execute("""
                    UPDATE join_requests SET status='approved' WHERE id=$1
                """, request_id)
                
                self.app.notify(f"Approved {req['username']}'s request")
            else:
                await conn.execute("""
                    UPDATE join_requests SET status='rejected' WHERE id=$1
                """, request_id)
                
                self.app.notify(f"Rejected {req['username']}'s request")
            
            await self.app.load_data()
            self.app.pop_screen()
        except Exception as e:
            self.app.notify(f"Error: {str(e)}")
        finally:
            await conn.close()

class ManageTeamScreen(Screen):
    """Manage team screen (owner only)"""
    
    CSS = """
    ManageTeamScreen {
        align: center middle;
    }
    
    #manage_container {
        width: 80;
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
    
    .section-title {
        text-style: bold;
        color: $accent;
        margin: 2 0 1 0;
    }
    
    .info {
        margin: 1 0;
    }
    
    .member-card {
        border: solid $primary;
        padding: 1;
        margin: 1 0;
        background: $panel;
    }
    
    .member-info {
        width: 1fr;
    }
    
    Button {
        margin: 1;
    }
    """
    
    def __init__(self, team_data, members):
        super().__init__()
        self.team_data = team_data
        self.members = members
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="manage_container"):
            yield Label("Manage Team", classes="title")
            yield Label(f"[bold cyan]Team Number:[/] {self.team_data['team_number']}", classes="info")
            yield Label(f"[bold cyan]Team Name:[/] {self.team_data['team_name']}", classes="info")
            yield Label(f"[bold cyan]Location:[/] {self.team_data['location']}", classes="info")
            yield Label(f"[bold cyan]Website:[/] {self.team_data['website']}", classes="info")
            
            yield Label("Team Members", classes="section-title")
            for member in self.members:
                role = "Creator" if member['username'] == self.team_data['creator'] else "Member"
                with Horizontal(classes="member-card"):
                    yield Label(f"👤 {member['username']} - {role}", classes="member-info")
                    if member['username'] != self.team_data['creator']:
                        yield Button("✗", variant="error", id=f"kick_{member['username']}")
            
            yield Button("Close", variant="default", id="close_btn")
    
    @on(Button.Pressed)
    async def handle_button(self, event: Button.Pressed):
        button_id = event.button.id
        
        if button_id == "close_btn":
            self.app.pop_screen()
        elif button_id.startswith("kick_"):
            username = button_id.split("_", 1)[1]
            result = await self.app.push_screen_wait(
                ConfirmKickScreen(username, self.team_data['team_number'])
            )
            if result:
                self.app.notify(f"Kicked {username} from the team")
                await self.app.load_data()
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
        self.team_members = []
        self.team_members = []
    
    def on_mount(self) -> None:
        """Called when app is mounted"""
        self.username = get_user()
        if not self.username:
            self.push_screen(LoginScreen())
        else:
            asyncio.create_task(self.load_data())
    
    async def load_data(self):
        """Load the team's data via postgres"""
        conn = await get_database_connection()
        
        team = await conn.fetchrow("""
            SELECT t.team_number, t.team_name, t.location, t.website, t.creator
            FROM teams t
            JOIN team_members m ON t.team_number = m.team_number
            WHERE m.username=$1
        """, self.username)
        
        if team:
            self.team_data = dict(team)
            self.is_owner = team['creator'] == self.username
            
            # Get team members
            # Get team members
            members = await conn.fetch("""
                SELECT username
                FROM team_members
                WHERE team_number=$1
            """, team['team_number'])
            self.team_members = [dict(m) for m in members]
            
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
        yield Vertical(id="menu_container")
        yield Footer()
    
    def rebuild_menu(self):
        """
        Rebuild the menu buttons based on the current state
        """
        
        menu = self.query_one("#menu_container", Vertical)
        menu.remove_children()
        
        if not self.team_data:
            menu.mount(Button("Join Team", id="join_team", variant="primary"))
            menu.mount(Button("Create Team", id="create_team", variant="success"))
        else:
            menu.mount(Button("View Team", id="view_team", variant="primary"))
            if self.is_owner:
                menu.mount(Button("Manage Team", id="manage_team", variant="success"))
            menu.mount(Button("Leave Team", id="leave_team", variant="error"))
            
        menu.mount(Button("Settings", id="settings", variant="default"))
        menu.mount(Button("More", id="more", variant="default"))
        
        # Reset focus to the first button after rebuilding
        buttons = menu.query(Button)
        if buttons:
            buttons.first().focus()
    
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
                
            # rebuild the menu along with the proper buttons
            self.rebuild_menu()
            
        except Exception:
            pass
    
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
            self.push_screen(ViewTeamScreen(
                self.team_data, 
                self.team_members, 
                self.pending_requests if self.is_owner else []
            ))
    
    @on(Button.Pressed, "#manage_team")
    async def handle_manage_team(self):
        """Manage a team (owner only)"""
        if self.team_data and self.is_owner:
            self.push_screen(ManageTeamScreen(self.team_data, self.team_members))
    
    @on(Button.Pressed, "#leave_team")
    async def handle_leave_team(self):
        """Handles leaving a team"""
        if not self.team_data:
            return
        
        conn = await get_database_connection()
        try:
            await conn.execute("""
                DELETE FROM team_members
                WHERE team_number=$1 AND username=$2
            """, self.team_data['team_number'], self.username)
            
            self.team_data = None
            self.is_owner = False
            self.pending_requests = []
            self.team_members = []
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
