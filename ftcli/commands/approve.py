import typer
import asyncio
from ftcli.database import get_database_connection

class Approve:
    """
    Class to send approval reqeust of a members to creator of team
    """
    def __init__(self):
        self.App = typer.Typer()
        @self.App.command()
        def request(request_id: int, allowed: bool):
            asyncio.run(self._request(request_id, allowed))
            
    async def _request(self, request_id: int, allowed: bool) -> None:
        """
        Docstring for sending approval request
        
        :param self: Gets the class attributes required
        :param request_id: Unique request id for identification
        :type request_id: int
        :param allowed: Type for checking whether the user is allowed to join
        :type allowed: bool
        """
        conn = await get_database_connection()
        
        req = await conn.fetchrow(
            "SELECT * FROM join_requests WHERE id=$1", request_id
        )
        
        if not req:
            print("Request not found")
            await conn.close()
            return
        
        if allowed:
            await conn.execute("""
                INSERT INTO team_members (team_member, username)
                VALUES ($1, $2)
            """, req["team_number"], req["username"])
            
            await conn.execute("""
                UPDATE join_requests SET status='approved' WHERE id=$1
            """, request_id)
            
            print("Approved")
        else:
            await conn.execute("""
                UPDATE join_requests SET status='rejected' WHERE id=$1
            """, request_id)
        
        await conn.close()
