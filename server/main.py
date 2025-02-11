from server import Server
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
}

if __name__ == '__main__':
    server = Server(db_config=db_config)
    asyncio.run(server.start())
