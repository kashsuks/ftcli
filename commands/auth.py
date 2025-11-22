import typer
import asyncio
from auth import createUser, authenticate, setUser, clear, getUser

class Auth:
    """
    Something
    """
    def __init__(self):
        self.App = typer.Typer()
        
        @self.App.command()
        def register():
            """
            Register a new user account
            """
            username = typer.prompt("Username")
            password = typer.prompt("Password", hide_input=True)
            confirm = typer.prompt("Confirm password", hide_input=True)
            
            if password != confirm:
                print("Passwords don't match!")
                return
            
            if len(password) < 6:
                print("Password must be at least 6 characters")
                return
            
            asyncio.run(createUser(username, password))
            
        @self.App.command()
        def login():
            """
            Login to your account
            """
            
            username = typer.prompt("Username")
            password = typer.prompt("Password", hide_input=True)
            
            if asyncio.run(authenticate(username, password)):
                setUser(username)
                print(f"Successfully logged in as {username}")
            else:
                print("Invalid username or password!")
                
        @self.App.command()
        def logout():
            """
            Logout from your account
            """
            
            clear()
            print("Logged out successfully")
            
        @self.App.command()
        def whoami():
            """
            Show current logged in user
            """
            
            user = getUser()
            if user:
                print(f"Logged in as: {user}")
            else:
                print("Not logged in")