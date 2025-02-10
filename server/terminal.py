from repository import Repository


class Terminal:
    def __init__(self, repository: Repository):
        self.repository = repository
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

    def get_commands(self):
        return f'Доступные команды: {', '.join(self.commands.keys())}'

    def processing_commands(self, command: str):
        """Функция проверяет и обрабатывает введенную команду."""
        if command in self.commands:
            return self.commands[command]()
        else:
            return "Такой команды не существует."

    def create_vm(self):
        pass

    def update_vm(self):
        pass

    def get_vm(self):
        pass

    def get_all_vms(self):
        pass

    def get_authenticated_vms(self):
        pass

    def get_connected_vms(self):
        pass

    def get_disk(self):
        pass

    def connect_vm(self):
        pass

    def disconnect_vm(self):
        pass
