from utils.enum.permission import Permission


class Command:

    def __init__(self, command: str, active: bool, message: str, permission: Permission, cooldown_seconds: int):
        self.command: str = command
        self.active: bool = active
        self.message: str = message
        self.permission: Permission = permission
        self.cooldown_seconds: int = cooldown_seconds
