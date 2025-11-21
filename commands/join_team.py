from textual.cli import command
from db import getDB

@command("join-team")
async def joinTeam(teamNumber: int, username: str, passcode: str):
    conn = await getDB()
    
    team = await conn.fetchrow("SELECT passcode FROM teams WHERE team_number=$1", teamNumber)
    if not team:
        print("Team does not exist.")
        return
    
    if team["passcode"] != passcode:
        print("Incorrect passcode.")
        return
    
    await conn.execute("""
        INSERT INTO join_requests (team_numver, username)
        VALUES ($1,$2)
    """, teamNumber, username)
    
    await conn.close()
    print("Join request submitted.")