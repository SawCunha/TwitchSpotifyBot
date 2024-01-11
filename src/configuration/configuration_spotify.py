class ConfigurationSpotify:
    def __init__(self, active, client_id, secret, username) -> None:
        self.active: bool = active
        self.client_id = client_id
        self.secret = secret
        self.username = username
