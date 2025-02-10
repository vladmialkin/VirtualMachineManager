import asyncio
import json

BUFF = 1024


class Disk:
    def __init__(self, size: int, uid: str):
        self.uid = uid
        self.size = size

    def __str__(self):
        return f"Диск: {self.uid}, размер: {self.size}"


class VirtualMachineClient:
    def __init__(self, host: str, port: int, uid: str, ram: int, cpu: int, disks: list[Disk], password: str):
        self.host = host
        self.port = port
        self.running = False

        self.uid = uid
        self.ram = ram
        self.cpu = cpu
        self.disks = disks

        self.__password = password
        self.is_auth = False
        self.is_conn = False

        self.command_list = {
            "vm_info": self.vm_info,
            "vm_info_json": self.vm_info_json,
            "help": self.help,
            "exit": self.stop,
            "con_server": self.connect_server,
        }

    def disk_size(self) -> int:
        return sum([disk.size for disk in self.disks])

    def authenticate(self):
        password = input("Введите пароль: ")
        if password == self.__password:
            self.is_auth = True
        else:
            print("Неверный пароль.")

    async def start(self):
        self.running = True
        while self.running:
            if self.is_auth:
                command = input(f"Команда: ")
                result = await self.commands(command.lower())
                print(result)
            else:
                self.authenticate()

    async def stop(self):
        self.running = False
        print("Клиент остановлен")

    async def commands(self, command: str):
        if command in self.command_list.keys():
            func = self.command_list[command]
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func()
                else:
                    result = func()
                return {"command": command, "result": result}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": "Такой команды не существует."}

    def help(self):
        commands = " ".join(self.command_list.keys())
        return f"Команды сервера:\n{commands}"

    def vm_info(self):
        return f"""
        Виртуальная машина: {self.uid}
        RAM: {self.ram}
        CPU: {self.cpu}
        Размер дисков: {self.disk_size()}
        Диски: {[str(disk) for disk in self.disks]}"""

    def vm_info_json(self):
        return {
            "uid": self.uid,
            "ram": self.ram,
            "cpu": self.cpu,
            "disks": [{
                "uid": disk.uid,
                "size": disk.size
            } for disk in self.disks]
        }

    async def connect_server(self):
        try:
            print("Соединение с сервером установлено.")
            reader, writer = await asyncio.open_connection(self.host, self.port)
            self.is_conn = True
            print("Введите команду сервера(для выхода напишите disconnect).")

            data = (await reader.read(BUFF)).decode()

            result = await self.commands(str(data))
            writer.write(json.dumps(result))

            await writer.drain()

            while self.is_conn:
                message = input()
                if message == "disconnect":
                    print("Отключение от сервера.")
                    break


        except Exception as e:
            print(f"Ошибка подключения к серверу: {str(e)}")
