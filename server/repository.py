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

    # async def update_vm(self, data):
    #     """Обновление данных ВМ"""
    #     async with self.pool.acquire() as conn:
    #         try:
    #             await conn.execute(
    #                 """
    #                 UPDATE virtual_machines
    #                 SET ram=$2, cpu=$3
    #                 WHERE id=$1 AND is_authorized=TRUE
    #                 """,
    #                 data["id"],
    #                 int(data["ram"]),
    #                 int(data["cpu"]),
    #             )
    #             logger.info(f"Виртуальная машина {data['id']} была обновлена.")
    #         except Exception as e:
    #             logger.error(f"Ошибка обновления ВМ: {str(e)}")
    #
    # async def list_disks(self):
    #     """Список всех жестких дисков"""
    #     async with self.pool.acquire() as conn:
    #         try:
    #             disks = await conn.fetch(
    #                 """SELECT d.*, vm.id as vm_id FROM disks d
    #                 LEFT JOIN virtual_machines vm
    #                 ON d.vm_id = vm.id"""
    #             )
    #             logger.info("Список дисков получен успешно.")
    #             return disks
    #         except Exception as e:
    #             logger.error(f"Ошибка при получении списка дисков: {str(e)}")
    #             return f"Ошибка при получении списка дисков: {str(e)}"
    #
    # async def add_disk(self, data):
    #     """Добавление нового диска в ВМ"""
    #     async with self.pool.acquire() as conn:
    #         try:
    #             disk_id = await conn.fetchval(
    #                 """
    #                 INSERT INTO disks (id, vm_id, size)
    #                 VALUES (gen_random_uuid(), $1, $2)
    #                 RETURNING id""",
    #                 data["vm_id"],
    #                 data["size"]
    #             )
    #             logger.info(f"Диск {disk_id} добавлен в виртуальную машину {data['vm_id']}.")
    #             return f"Диск {disk_id} добавлен в виртуальную машину {data['vm_id']}"
    #         except Exception as e:
    #             logger.error(f"Ошибка при добавлении диска: {str(e)}")
    #             return f"Ошибка при добавлении диска: {str(e)}"
    #
    # async def update_disk(self, data):
    #     """Обновление данных диска"""
    #     async with self.pool.acquire() as conn:
    #         try:
    #             await conn.execute(
    #                 """
    #                 UPDATE disks
    #                 SET vm_id=$2, size=$3
    #                 WHERE id=$1
    #                 """,
    #                 data["id"],
    #                 data["vm_id"],
    #                 int(data["size"]),
    #             )
    #             logger.info(f"Диск {data['id']} был обновлен.")
    #             return f"Диск {data['id']} был обновлен."
    #         except Exception as e:
    #             logger.error(f"Ошибка обновления диска: {str(e)}")
    #             return f"Ошибка обновления диска: {str(e)}"
