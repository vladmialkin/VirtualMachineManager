from server import Server
import asyncio

if __name__ == '__main__':
    server = Server()
    asyncio.run(server.start())
