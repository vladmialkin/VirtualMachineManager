import asyncio

from server_terminal import TerminalServer

MAX_READ = 1024


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 2001):
        self.host = host
        self.port = port
        self.server = None
        self.terminal_server = TerminalServer(server=self)
        self.__is_working = False

    @property
    def is_working(self):
        return self.__is_working

    async def start(self):
        """Функция запускает сервер"""
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        self.is_running = True

        addr = self.server.sockets[0].getsockname()
        print(f"Сервер запущен на {addr}")

        try:
            async with self.server:
                await self.server.serve_forever()
        except KeyboardInterrupt:
            await self.stop()

    async def stop(self):
        """Функция останавливает сервер"""
        if self.is_running:
            self.is_running = False
            self.server.close()
            await self.server.wait_closed()
            print("Сервер остановлен.")

    async def handle_client(self, reader, writer):
        """Функция ждет подключения клиентов"""
        addr = writer.get_extra_info('peername')
        print(f"Клиент {addr} подключился.")

        commands = self.terminal_server.get_available_commands()
        writer.write(f"Доступные команды: {commands}\n".encode())
        await writer.drain()

        while True:
            data = await reader.read(MAX_READ)
            if not data:
                print(f"Клиент {addr} отключился.")
                break

            message = data.decode()
            print(f"Получены данные {message} от {addr}")

            result = self.terminal_server.handle_command(message.strip())

            writer.write(result.encode())
            await writer.drain()

        print("Закрытие соединения.")
        writer.close()
