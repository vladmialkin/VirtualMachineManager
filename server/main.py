from server import Server
import asyncio

db_config = {
    "user": "postgres",
    "password": "postgres",
    "database": "postgres",
    "host": "127.0.0.1",
    "port": 5432,
}

if __name__ == '__main__':
    server = Server(db_config=db_config)
    asyncio.run(server.start())
