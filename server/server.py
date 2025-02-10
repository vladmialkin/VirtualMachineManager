import asyncio
import logging

from repository import Repository
from terminal import Terminal

BUFF = 1024

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Server:
    def __init__(self, host: str = "127.0.0.1", port: int = 8888, db_config=None):
        self.host = host
        self.port = port

        self.repository = Repository(db_config)
        self.terminal = Terminal(
            repository=self.repository
        )

        self.server = None

        self.active_vm = {}
        self.authenticated_vm = {}

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = self.server.sockets[0].getsockname()
        logging.info(f"Сервер запущен на {addr}")
        await self.repository.connect()
        try:
            async with self.server:
                await self.server.serve_forever()
        except KeyboardInterrupt:
            await self.stop()

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        logging.info("Сервер остановлен.")

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info(f"Клиент {addr} подключился.")

        await self.write_commands(writer)

        while True:
            message = (await reader.read(BUFF)).decode()
            if not message:
                logging.info(f"Клиент {addr} отключился.")
                break

            logging.info(f"Получена команда {message} от {addr}")

            response = self.terminal.processing_commands(message)
            writer.write(response.encode())
            await writer.drain()
            logging.info(f"Ответ отправлен клиенту {addr}")

        logging.info("Закрытие соединения.")
        writer.close()

    async def write_commands(self, writer):
        """Функция отправляет доступные команды сервера."""
        writer.write(self.terminal.get_commands().encode())
        await writer.drain()
        logging.info(f"Отправлены доступные команды сервера.")
