import asyncio


class TerminalServer:
    def __init__(self, server):
        self.server = server
        self.commands = {
            'status': self.status,
            'commands': self.get_available_commands
        }

    def handle_command(self, command):
        """Обрабатывает команду от клиента."""
        command = command.strip().lower()
        if command in self.commands:
            return self.commands[command]()
        else:
            return f"Команда '{command}' не распознана."

    def status(self):
        """Показывает статус сервера."""
        return "Сервер работает."

    def get_available_commands(self):
        """Возвращает список доступных команд."""
        return f"{', '.join(list(self.commands.keys()))}"
