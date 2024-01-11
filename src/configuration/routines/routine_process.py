import configparser
from configuration.routines.routine import Routine
from utils.enum.permission import get_permission


def process_routines():
    config = configparser.ConfigParser()
    routines: [] = []
    with open('./data/routines.ini') as file:
        config.read_file(file)
        for section in config.sections():
            routine = _Process_routine(section, config)
            routines.append(routine)

    return routines


def _Process_routine(section: str, config):
    active: bool = config.getboolean(section, 'active', fallback=False)
    message: str = config.get(section, 'message', fallback=None)
    time_minutes: int = config.getint(section, 'time_minutes', fallback=10)
    return Routine(section.lower(), active, message, time_minutes)
