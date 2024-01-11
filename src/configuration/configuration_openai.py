class ConfigurationOpenAi:
    def __init__(self, active: bool, api_key: str, gpt_model: str) -> None:
        self.active: bool = active
        self.api_key: str = api_key
        self.gpt_model: str = gpt_model
