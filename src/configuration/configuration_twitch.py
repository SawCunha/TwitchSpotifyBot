class ConfigurationTwitch:
    def __init__(self, my_app_id: str, my_app_secret: str, channel: str, commands: [], routines: []):
        self.my_app_id: str = my_app_id
        self.my_app_secret: str = my_app_secret
        self.channel: str = channel
        self.commands: [] = commands
        self.routines: [] = routines
