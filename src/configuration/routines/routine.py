from utils.enum.permission import Permission


class Routine:

    def __init__(self, routine: str, active: bool, message: str, time_minutes: int):
        self.routine: str = routine
        self.active: bool = active
        self.message: str = message
        self.time_minutes: int = time_minutes
