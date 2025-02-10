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
            'create_vm': self.create_vm,
            'update_vm': self.update_vm,
            'get_vm': self.get_vm,
            'get_all_vms': self.get_all_vms,
            'get_authenticated_vms': self.get_authenticated_vms,
            'get_connected_vms': self.get_connected_vms,
            'get_disk': self.get_disk,
            'connect_vm': self.connect_vm,
            'disconnect_vm': self.disconnect_vm,
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
                print(result)
                if result:
                    client = VirtualMachineClient(
                        uid=result[0],
                        ram=result[1],
                        cpu=result[2],
                        disks=None,
                        password=result[3]
                    )
                    await client.connect_server()
                    self.server.active_vms.update({client.uid: client})
                    return "Виртуальная машина создана и запущена."

            else:
                logging.info(f"Неверные параметры. Повторите ввод параметров.")

    def update_vm(self, **params):
        pass

    def get_vm(self, **params):
        pass

    def get_all_vms(self, **params):
        return "\n".join(str(vm) for vm in self.server.all_vms)

    def get_authenticated_vms(self, **params):
        pass

    def get_connected_vms(self, **params):
        pass

    def get_disk(self, **params):
        pass

    def connect_vm(self, **params):
        pass

    def disconnect_vm(self, **params):
        pass

    async def __create_vms(self, **params):
        """Функция создает и запускает клиенты ВМ."""
        vms_list = self.repository.get_all_vms()
        print(vms_list)
        # for vm in vms_list:
        #     obj = VirtualMachine(
        #         vm_id='1',
        #         ram=2,
        #         cpu=3,
        #         disks=[Disk(uid="1", size=2) for disk in vm['disks']],
        #         password='4',
        #     )
        #     self.all_vms.update({obj.vm_id: obj})
