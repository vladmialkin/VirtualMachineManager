import asyncio
import hashlib
import logging

from repository import Repository
from client import VirtualMachineClient, Disk

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
            'connect_vm': self.connect_vm,
            'get_all_vms': self.get_all_vms,
            'get_auth_vms': self.get_auth_vms,
            'get_active_vms': self.get_active_vms,
            'create_disk': self.create_disk,
            'get_all_disks': self.get_all_disks,

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
                        name=result[1],
                        ram=result[2],
                        cpu=result[3],
                        disks=None,
                        password=result[4]
                    )
                    self.server.all_vms.update({client.name: client})
                    return "Виртуальная машина создана и запущена."

            else:
                logging.info(f"Неверные параметры. Повторите ввод параметров.")

    async def update_vm(self, writer, reader):
        writer.write(
            "Введите имя ВМ для обновления данных.(break для отмены)".encode())
        await writer.drain()

        client_name = (await reader.read(BUFF)).decode()
        if not client_name:
            logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
            return "Не удалось получить данные от клиента."

        elif client_name == "break":
            return "Отмена команды."

        if client_name in self.server.active_vms:
            client = self.server.active_vms[client_name]

            while True:
                writer.write("Введите новые данные(name, ram, cpu)".encode())
                await writer.drain()

                message = (await reader.read(BUFF)).decode()
                if not message:
                    logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
                    return "Не удалось получить данные от клиента."

                elif message == "break":
                    return "Отмена команды."

                data = message.split()
                name = data[0]
                ram = int(data[1])
                cpu = int(data[2])
                result = await self.repository.update_vm(uid=client.uid, ram=ram, cpu=cpu, name=name)
                if result:
                    client.update(name=name, ram=ram, cpu=cpu)
                    return "ВМ обновлена."
                else:
                    return "ВМ не удалось обновить."
        else:
            return "ВМ не активна."
    def get_all_vms(self, **params):
        """Функция выводит список всех ВМ."""
        if self.server.all_vms:
            return "Все ВМ: " + ", ".join(vm.vm_info() for vm in self.server.all_vms.values())
        return "Нет доступных ВМ."

    def get_auth_vms(self, **params):
        """Функция выводит список авторизованных ВМ."""
        if self.server.authenticated_vms:
            return "Авторизованные ВМ: " + ", ".join(vm.vm_info() for vm in self.server.authenticated_vms.values())
        return "Нет авторизованных ВМ."

    def get_active_vms(self, **params):
        """Функция выводит список активных ВМ."""
        if self.server.active_vms:
            return "Активные ВМ: " + ", ".join(vm.vm_info() for vm in self.server.active_vms.values())
        return "Нет активных ВМ."

    async def create_disk(self, writer, reader):
        while True:
            writer.write(
                "Введите параметры размер диска и имя виртуальной машины(size, name).(break для отмены)".encode())
            await writer.drain()

            message = (await reader.read(BUFF)).decode()
            if not message:
                logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
                return "Не удалось получить данные от клиента."

            elif message == "break":
                return "Отмена команды."

            if len(message.split()) == 2:
                size = int(message.split()[0])
                vm_name = message.split()[1]
                if vm_name not in self.server.all_vms:
                    continue

                result = await self.repository.add_disk(size=size, vm_name=vm_name)
                if result:
                    disk = Disk(uid=result[0], size=int(result[1]))
                    client = self.server.all_vms[vm_name]
                    client.add_disk(disk)
                    return f"Диск добавлен в ВМ {client.name}"

            else:
                logging.info(f"Неверные параметры. Повторите ввод параметров.")

    async def get_all_disks(self, **params):
        disks = await self.repository.get_all_disks()
        if disks:
            return "".join(
                f"""id: {disk[0]}\nsize: {disk[1]}\nvm_id: {disk[2]}\nvm_name: {disk[3]}\nvm_ram: {disk[4]}\nvm_cpu: {disk[5]}\n\n"""
                for disk in disks)
        else:
            return "Нет дисков."

    async def start_vm(self, writer, reader):
        """Функция запускает ВМ."""
        while True:
            writer.write(
                "Введите имя ВМ.(break для отмены)".encode())
            await writer.drain()

            message = (await reader.read(BUFF)).decode()
            if not message:
                logging.info(f"Клиент {writer.get_extra_info('peername')} отключился.")
                return "Не удалось получить данные от клиента."

            if message == "break":
                return "Отмена команды."

            if message in self.server.all_vms:
                client = self.server.all_vms[message]
                self.server.active_vms.update({client.name: client})
                return "Виртуальная машина запущена."
            else:
                logging.info(f"Неверные параметры. Повторите ввод параметров.")
                return "Нет такой ВМ."

    async def connect_vm(self, writer, reader):
        """Функция подключается к ВМ."""
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
            client = self.server.active_vms[client_name]

            while True:
                if not client.is_auth:
                    writer.write("Введите пароль: ".encode())
                    await writer.drain()

                    password = (await reader.read(BUFF))

                    if password == "break":
                        return "Выход из ВМ."

                    result = await client.authenticate(password)
                    writer.write(result.encode())
                    await writer.drain()

                    commands_info = client.help()
                    writer.write(commands_info.encode())
                    await writer.drain()

                else:
                    writer.write("ВМ авторизована.".encode())
                    await writer.drain()
                    break
            while True:
                if not client.is_auth:
                    break
                self.server.authenticated_vms.update({client.name: client})
                command = (await reader.read(BUFF)).decode()
                if not command:
                    break

                if command == "logout":
                    self.server.authenticated_vms.pop(client.name)

                if command == "break":
                    return "Выход из ВМ."

                response = await client.commands(command)
                writer.write(response.encode())
                await writer.drain()
            return "Выход из ВМ."
        else:
            return "Неверное имя ВМ."

    async def create_vms(self, **params):
        """Функция создает и запускает клиенты ВМ."""
        vms_list = await self.repository.get_all_vms()
        for vm in vms_list:
            disks = await self.repository.get_disks_in_vm(vm[0])
            client = VirtualMachineClient(
                uid=vm[0],
                name=vm[1],
                ram=vm[2],
                cpu=vm[3],
                disks=[Disk(uid=disk[0], size=disk[1]) for disk in disks],
                password=vm[4],
            )
            self.server.all_vms.update({client.name: client})
        logging.info(f"ВМ найдены: {len(vms_list)}")
