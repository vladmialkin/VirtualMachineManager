import asyncio
import hashlib
import logging

from repository import Repository
from virtual_machine import VirtualMachine, Disk
from client import VirtualMachineClient

BUFF = 1024


class Terminal:
    def __init__(self, repository: Repository, server):
        self.repository = repository
        self.server = server
        self.commands = {
            'get_commands': self.get_commands,
            'start_vm': self.start_vm,
            'create_vm': self.create_vm,
            'update_vm': self.update_vm,
            'get_vm': self.get_vm,
            'get_all_vms': self.get_all_vms,
            'get_auth_vms': self.get_auth_vms,
            'get_active_vms': self.get_active_vms,
            'get_disk': self.get_disk,
            'connect_vm': self.connect_vm,
        }

    def get_commands(self, **params):
        return f'Доступные команды: {', '.join(self.commands.keys())}'

    async def processing_commands(self, command: str, **params):
        """Функция проверяет и обрабатывает введенную команду."""
        if command in self.commands:
            func = self.commands[command]
            if asyncio.iscoroutinefunction(func):
                return await func(**params)
            else:
                return func(**params)
        else:
            return "Такой команды не существует."

    async def create_vm(self, writer, reader):
        """Функция добавляет новую ВМ в БД."""
        while True:
            writer.write(
                "Введите параметры новой ВМ через пробел: ram, cpu, name, password.(break для отмены)".encode())
            await writer.drain()

            message = (await reader.read(BUFF)).decode()
            if not message:
                logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
                return "Не удалось получить данные от клиента."

            elif message == "break":
                return "Отмена команды."

            if len(message.split()) == 4:
                data = message.split()
                ram = int(data[0])
                cpu = int(data[1])
                name = data[2]
                password_hash = hashlib.sha256(data[3].encode()).hexdigest()

                result = await self.repository.create_vm(ram=ram, cpu=cpu, name=name, password=password_hash)
                if result:
                    client = VirtualMachineClient(
                        uid=result[0],
                        ram=result[1],
                        cpu=result[2],
                        disks=None,
                        password=result[3]
                    )
                    await client.connect_server()
                    self.server.active_vms.update({client.name: client})
                    return "Виртуальная машина создана и запущена."

            else:
                logging.info(f"Неверные параметры. Повторите ввод параметров.")

    def update_vm(self, **params):
        pass

    def get_vm(self, **params):
        pass

    def get_all_vms(self, **params):
        if self.server.all_vms:
            return "Все ВМ: " + ", ".join(str(vm) for vm in self.server.all_vms)
        return "Нет доступных ВМ."

    def get_auth_vms(self, **params):
        if self.server.authenticated_vms:
            return "Авторизованные ВМ: " + ", ".join(str(vm) for vm in self.server.authenticated_vms)
        return "Нет авторизованных ВМ."

    def get_active_vms(self, **params):
        if self.server.active_vms:
            return "Активные ВМ: " + ", ".join(str(vm) for vm in self.server.active_vms)
        return "Нет активных ВМ."

    def get_disk(self, **params):
        pass

    async def start_vm(self, writer, reader):
        while True:
            writer.write(
                "Введите имя ВМ.(break для отмены)".encode())
            await writer.drain()

            message = (await reader.read(BUFF)).decode()
            if not message:
                logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
                return "Не удалось получить данные от клиента."

            elif message == "break":
                return "Отмена команды."

            if message in self.server.all_vms:
                client = self.server.all_vms.pop(message)
                asyncio.create_task(client.connect_server())
                self.server.active_vms.update({client.name: (client, writer, reader)})
                return "Виртуальная машина запущена."

            else:
                logging.info(f"Неверные параметры. Повторите ввод параметров.")

    async def connect_vm(self, writer, reader):
        # await self.start_vm(writer, reader)

        writer.write(
            "Введите имя ВМ.(break для отмены)".encode())
        await writer.drain()

        client_name = (await reader.read(BUFF)).decode()
        if not client_name:
            logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
            return "Не удалось получить данные от клиента."

        elif client_name == "break":
            return "Отмена команды."

        if client_name in self.server.active_vms:
            client = self.server.active_vms[client_name][0]

            while True:
                if not client.is_auth:
                    writer.write("Введите пароль: ".encode())
                    await writer.drain()

                    password = (await reader.read(BUFF))
                    result = await client.authenticate(password)
                    writer.write(result.encode())
                    await writer.drain()

                    commands_info = client.help()
                    writer.write(commands_info.encode())
                    await writer.drain()

                else:

                    command = (await reader.read(BUFF)).decode()
                    if not command:
                        break

                    if command == "break":
                        return "Выход из ВМ."

                    response = await client.commands(command)
                    writer.write(response.encode())
                    await writer.drain()

        else:
            return "Неверное имя ВМ."

    async def create_vms(self, **params):
        """Функция создает и запускает клиенты ВМ."""
        vms_list = await self.repository.get_all_vms()
        for vm in vms_list:
            client = VirtualMachineClient(
                uid=vm[0],
                name=vm[1],
                ram=vm[2],
                cpu=vm[3],
                disks=None,
                password=vm[4],
            )
            # TODO добавить создание дисков
            self.server.all_vms.update({client.name: client})
        logging.info(f"ВМ найдены: {len(vms_list)}")
