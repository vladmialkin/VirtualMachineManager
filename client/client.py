import asyncio


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

        self.command_list = {
            "vm_info": self.vm_info,
            "help": self.help,
            "exit": self.stop
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
                await self.commands(command.lower())
            else:
                self.authenticate()

    async def stop(self):
        self.running = False
        print("Клиент остановлен")

    async def send_message(self, command: str):
        pass

    async def commands(self, command: str):
        match command:
            case "exit":
                await self.stop()
            case "help":
                self.help()
            case "vm_info":
                self.vm_info()

    def help(self):
        commands = " ".join(self.command_list.keys())
        print(f"Команды сервера:\n{commands}")

    def vm_info(self):
        info = f"""Виртуальная машина: {self.uid}\nRAM: {self.ram}\nCPU: {self.cpu}\nДиски: {[str(disk) for disk in self.disks]}"""
        print(info)
