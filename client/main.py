import asyncio

from client import AdminClient

if __name__ == "__main__":
    admin_client = AdminClient()
    asyncio.run(admin_client.connect_server())
