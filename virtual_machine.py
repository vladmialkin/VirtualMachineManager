import hashlib


class Disk:
    def __init__(self, size: int, uid: str):
        self.uid = uid
        self.size = size

    def __str__(self):
        return f"Диск: {self.uid}, размер: {self.size}"


class VirtualMachine:
    def __init__(self, vm_id: str, ram: int, cpu: int, disks: list[Disk], password="password"):
        self.vm_id = vm_id
        self.ram = ram
        self.cpu = cpu
        self.disks = disks
        self.password_hash = self.hash_password(password)

    def hash_password(self, password: str):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str):
        return self.password_hash == self.hash_password(password)

    def get_size(self):
        return sum(disk.size for disk in self.disks)

    def get_info(self):
        return f"""
        Виртуальная машина: {self.uid}
        RAM: {self.ram}
        CPU: {self.cpu}
        Размер дисков: {self.get_size()}
        Диски: {[str(disk) for disk in self.disks]}"""
