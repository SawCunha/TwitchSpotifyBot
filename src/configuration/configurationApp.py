class ConfigurationApp:
    def __init__(self, log, dev, language) -> None:
        self.log: bool = log
        self.dev: bool = dev
        self.language: str = language
