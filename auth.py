import asyncio
import bcrypt
import typer

from database import get_database_connection

async def hash(password: str) -> str:
    """Hashes a password using bcrypt

    Args:
        password (str): User defined password

    Returns:
        str: The hashed version of the password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def verify(password: str, hashed: str) -> bool:
    """Verify the user password against the generated hash

    Args:
        password (str): The user generated password
        hashed (str): Hashed password

    Returns:
        bool: Whether password matches hash or not
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

async def create_user(username: str, password: str):
    """Create a new user account

    Args:
        username (str): The users username
        password (str): User password
    """
    
    conn = await get_database_connection()
    
    #check if the user already exists
    existing = await conn.fetchrow(
        "SELECT username FROM users WHERE username=$1", username
    )
    
    if existing:
        print("Username already exists!")
        await conn.close()
        return False
    
    hashed = await hash(password)
    await conn.execute("""
        INSERT INTO users (username, password_hash)
        VALUES ($1,$2)
    """, username, hashed)
    
    print(f"User '{username}' has been created successfully!")
    await conn.close()
    return True

async def authenticate(username: str, password: str) -> bool:
    """Authenticate the user

    Args:
        username (str): _description_
        password (str): _description_

    Returns:
        bool: _description_
    """
    
    conn = await get_database_connection()
    
    user = await conn.fetchrow(
        "SELECT password_hash FROM users WHERE username=$1", username
    )
    
    await conn.close()
    
    if not user:
        return False
    
    return await verify(password, user['password_hash'])

def get_user() -> str:
    """_summary_

    Returns:
        str: _description_
    """
    
    try:
        with open('.ftcli_session', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def set_user(username: str):
    """_summary_

    Args:
        username (str): _description_
    """
    with open('.ftcli_session', 'w') as f:
        f.write(username)

def clear():
    """
    Clear the current session
    """
    try:
        import os
        os.remove('.ftcli_session')
    except FileNotFoundError:
        pass