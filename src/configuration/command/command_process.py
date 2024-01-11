import configparser
from configuration.command.command import Command
from utils.enum.permission import get_permission


def process_commands():
    config = configparser.ConfigParser()
    commands: [] = []
    with open('./data/command.ini') as file:
        config.read_file(file)
        for section in config.sections():
            command = _Process_command(section, config)
            commands.append(command)

    return commands


def _Process_command(command: str, config):
    active: bool = config.getboolean(command, 'active', fallback=False)
    message: str = config.get(command, 'message', fallback=None)
    permission: str = config.get(command, 'permission', fallback='ALL')
    cooldown_seconds: int = config.getint(command, 'cooldown_seconds', fallback=10)
    return Command(command.lower(), active, message, get_permission(permission), cooldown_seconds)
