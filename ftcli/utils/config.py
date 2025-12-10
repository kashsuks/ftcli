"""
Used for fetching database url as a variable
"""

import os
from dotenv import load_dotenv # type: ignore
load_dotenv()
DB_URL = os.getenv("POSTGRES_URL")