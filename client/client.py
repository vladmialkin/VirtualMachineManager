import asyncio

MAX_READ = 1024


class Client:
    def __init__(self, host='127.0.0.1', port=2001):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            print(f'Подключение к серверу {self.host}:{self.port}')
        except Exception as e:
            print(f'Ошибка подключения: {e}')
            exit(1)

    async def send_message(self, message):
        if self.writer:
            self.writer.write(message.encode())
            await self.writer.drain()
            print(f'Отправлено: {message}')
        else:
            print('Нет соединения с сервером.')

    async def receive_message(self):
        buffer = ""
        while True:
            try:
                data = await self.reader.read(MAX_READ)
                if not data:
                    print('Закрыто соединение.')
                    break

                buffer += data.decode()
                while "\t\n\t\n" in buffer:
                    message, buffer = buffer.split("\t\n\t\n", 1)
                    print(str(message))
            except Exception as e:
                print(f'Ошибка при получении данных: {e}')
                break

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            print('Соединение закрыто.')

    async def run(self):
        await self.connect()
        while True:
            response = await self.reader.read(MAX_READ)
            if not response:
                break
            print(response.decode())
            message = input("Команда: ")
            self.writer.write(message.encode())
            await self.writer.drain()