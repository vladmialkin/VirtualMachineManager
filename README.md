# ТЗ
Задача: Создать клиент-серверное приложение на сокетах (asyncio, консольное приложение) менеджер виртуальных машин. Должен быть написан как сервер, так и клиент, работа должна быть продемонстрирована в виде нескольких подключений клиентов к серверу. Сервер должен как принимать команды от клиентов, так и обрабатывать свои внутренние команды.

Описание:
Вы разрабатываете систему учета виртуальных машин. Каждая виртуальная машина имеет:

Уникальный идентификатор (ID).
Объем выделенной RAM.
Количество выделенных CPU.
Объем памяти жесткого диска (Жесткий диск у ВМ может быть не один)
Уникальнный индентификатор жесткого диска(ID)

Пояснение: виртуальная машина это клиент

Задачи:
Разработать сервер который будет обращаться к клиентам 
На сервере разработайте класс, представляющий виртуальную машину.
Реализуйте аутентификацию при подключению к клиенту
Создайте метод для добавления новой виртуальной машины в базу данных.
Реализуйте метод, который выводит список всех подключенных виртуальных машин с их параметрами.
Реализуйте метод, который выводит список всех авторизованных виртуальных машин с их параметрами.
Реализуйте метод, который выводит список всех когда либо подключаемых виртуальных машин с их параметрами.

Реализуйте метод, который выходит из авторизованной ВМ.
Реализуйте метод, который обновляет данные в авторизованной ВМ.

Реализовать метод, который выводит список всех жестких дисков, с их параметрами(в том числе и с ВМ, к которой он привязан)

для хранения используйте PostgresSQL, все запросы нужно писать с использованием Asyncpg без каких-либо ОРМ.

Запишите видео работы приложения. Необходимо предоставить код, желательно на Git. Докер с запуском будет большим плюсом.

