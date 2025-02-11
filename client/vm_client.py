import asyncio
import hashlib
import logging

BUFF = 1024


class Disk:
    def __init__(self, size: int, uid: str):
        self.uid = uid
        self.size = size

    def __str__(self):
        return f"Диск: {self.uid}, размер: {self.size}"


class VirtualMachineClient:
    def __init__(self,
                 uid: str,
                 name: str,
                 ram: int,
                 cpu: int,
                 disks: list[Disk] | None,
                 password: str,
                 host: str = '127.0.0.1',
                 port: int = 8888):
        self.host = host
        self.port = port
        self.running = False

        self.uid = uid
        self.name = name
        self.ram = ram
        self.cpu = cpu
        self.disks = disks

        self.__password = password
        self.is_auth = False

        self.reader = None
        self.writer = None

        self.command_list = {
            "vm_info": self.vm_info,
            "help": self.help,
            "logout": self.logout,
            "stop_client": self.stop,
        }

    def disk_size(self) -> int:
        if self.disks:
            return sum([disk.size for disk in self.disks])
        else:
            return 0

    async def authenticate(self, password):
        if self.__password == hashlib.sha256(password).hexdigest():
            self.is_auth = True
            return "Вы авторизованы в ВМ.\n"
        else:
            return "Неверный пароль.\n"

    def logout(self):
        self.is_auth = False
        return "Вы вышли из ВМ.\n"

    async def stop(self):
        self.running = False
        logging.info("Клиент остановлен.")

    async def commands(self, command: str):
        if command in self.command_list.keys():
            func = self.command_list[command]
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func()
                else:
                    result = func()
                return result
            except Exception as e:
                return f"Возникла ошибка: {str(e)}\n"
        else:
            return "Такой команды не существует.\n"

    def help(self):
        commands = ", ".join(self.command_list.keys())
        return f"Команды ВМ: {commands}\n"

    def vm_info(self):
        if self.disks:
            disk = [str(disk) for disk in self.disks]
        else:
            disk = "Нет дисков"
        return f"""
        Виртуальная машина: {self.uid} {self.name}
        RAM: {self.ram}
        CPU: {self.cpu}
        Размер дисков: {self.disk_size()}
        Диски: {disk}\n"""

    def update(self,
               name: str | None = None,
               ram: int | None = None,
               cpu: int | None = None):
        if name:
            self.name = name
        if ram:
            self.ram = ram
        if cpu:
            self.cpu = cpu

    def add_disk(self, disk: Disk):
        if self.disks:
            self.disks.append(disk)
        else:
            self.disks = [disk]

    async def connect_server(self):
        # Функция является заглушкой...
        try:
            logging.info(f'Подключение к серверу {self.host}:{self.port}...')
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            logging.info('Подключение установлено!')

            # while True:
            #
            #
            #     command = (await self.reader.read(BUFF)).decode()
            #     logging.info(f'Получена команда от сервера: {command}')
            #     if command.lower() == "disconnect":
            #         logging.info('Завершение работы клиента...')
            #         break
            #
            #     writer.write(command.encode())
            #     await writer.drain()
            #     logging.info(f'Команда отправлена: {command}')
            #
            #     response = await reader.read(BUFF)
            #     logging.info(f'Получен ответ от сервера: {response.decode()}')

            self.writer.close()
            await self.writer.wait_closed()
            logging.info('Соединение закрыто.')

        except Exception as e:
            logging.error(f'Ошибка подключения к серверу: {str(e)}')
