import asyncio
import logging

BUFF = 1024

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AdminClient:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self.host = host
        self.port = port
        self.running = False

    async def connect_server(self):
        try:
            logging.info(f'Подключение к серверу {self.host}:{self.port}...')
            reader, writer = await asyncio.open_connection(self.host, self.port)
            logging.info('Подключение установлено!')

            response = await reader.read(BUFF)
            logging.info(f'Получен ответ от сервера: {response.decode()}')

            while True:
                command = input("Введите команду: ")

                if command.lower() == "exit":
                    logging.info('Завершение работы клиента...')
                    break

                writer.write(command.encode())
                await writer.drain()
                logging.info(f'Команда отправлена: {command}')

                response = await reader.read(BUFF)
                logging.info(f'Получен ответ от сервера: {response.decode()}')

            writer.close()
            await writer.wait_closed()
            logging.info('Соединение закрыто.')

        except Exception as e:
            logging.error(f'Ошибка подключения к серверу: {str(e)}')
