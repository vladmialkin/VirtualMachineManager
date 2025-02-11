import asyncpg
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, db_config):
        self.db_config = db_config
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**self.db_config)
        logger.info("Подключение к базе данных установлено")

    async def create_vm(self, ram: int, cpu: int, name: str, password: str):
        """Добавление новой ВМ"""
        async with self.pool.acquire() as conn:
            try:
                result = await conn.fetchrow(
                    """
                    INSERT INTO virtual_machines (ram, cpu, name, password_hash)
                    VALUES ( $1, $2, $3, $4)
                    RETURNING *
                    """, ram, cpu, name, password
                )
                if result:
                    logger.info(f"Виртуальная машина с UID {result['id']} успешно добавлена.")
                    return result
                else:
                    logger.error("Ошибка: Виртуальная машина не была добавлена.")
            except Exception as e:
                logger.error(f"Ошибка при добавлении ВМ: {str(e)}")
        return None

    async def get_all_vms(self):
        """Функция получает список всех ВМ."""
        async with self.pool.acquire() as conn:
            try:
                vms = await conn.fetch("SELECT * FROM virtual_machines")
                logger.info("Список виртуальных машин получен.")
                return vms
            except Exception as e:
                logger.error(f"Ошибка при получении списка ВМ: {e}")

    async def get_disks_in_vm(self, vm_uid: str):
        async with self.pool.acquire() as conn:
            try:
                disks = await conn.fetch("SELECT id, size FROM disks WHERE vm_id = $1", vm_uid)
                logger.info(f"Список дисков ВМ №{vm_uid}.")
                return disks
            except Exception as e:
                logger.error(f"Ошибка при получении списка дисков для ВМ №{vm_uid}: {e}")

    async def update_vm(self, uid: str, name: str, ram: int, cpu: int):
        """Обновление данных ВМ"""
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute("""
                                    UPDATE virtual_machines
                                    SET name = $1, ram = $2, cpu = $3
                                    WHERE id = $4
                                """, name, ram, cpu, uid)
                if result:
                    logger.info(f"Виртуальная машина {uid} была обновлена.")
                    return True
                else:
                    logging.warning(f"Виртуальная машина с ID {uid} не найдена.")
                    return False
            except Exception as e:
                logger.error(f"Ошибка обновления ВМ: {str(e)}")

    async def get_all_disks(self):
        """Список всех жестких дисков"""
        async with self.pool.acquire() as conn:
            try:
                disks = await conn.fetch(
                    """SELECT
            d.id AS disk_id,
            d.size AS disk_size,
            vm.id AS vm_id,
            vm.name AS vm_name,
            vm.ram AS vm_ram,
            vm.cpu AS vm_cpu,
            vm.password_hash AS vm_password_hash
        FROM
            disks d
        JOIN
            virtual_machines vm ON d.vm_id = vm.id;"""
                )
                logger.info("Список дисков получен успешно.")
                return disks
            except Exception as e:
                logger.error(f"Ошибка при получении списка дисков: {str(e)}")
                return f"Ошибка при получении списка дисков: {str(e)}"

    async def add_disk(self, vm_name: str, size: int):
        """Добавление нового диска в ВМ"""
        async with self.pool.acquire() as conn:
            try:
                vm = await conn.fetchrow("SELECT id FROM virtual_machines WHERE name = $1", vm_name)
                if vm is None:
                    return "Виртуальная машина с данным именем не найдена."
                result = await conn.fetchrow(
                    "INSERT INTO disks (vm_id, size) VALUES ($1, $2) RETURNING id, size",
                    vm[0], size
                )
                logger.info(f"Жесткий диск создан с ID: {result}")
                return result
            except Exception as e:
                logger.error(f"Ошибка при создании диска: {str(e)}")
                return f"Ошибка при добавлении диска: {str(e)}"
