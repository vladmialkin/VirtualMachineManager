import asyncio

from client import VirtualMachineClient, Disk

if __name__ == "__main__":
    client = VirtualMachineClient(host="127.0.0.1", port=2000, uid="vm_1", ram=2048, cpu=6, disks=[
        Disk(100, "disk_1"),
        Disk(250, "disk_2")
    ], password="123")
    asyncio.run(client.start())
