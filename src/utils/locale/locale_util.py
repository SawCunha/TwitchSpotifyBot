from pyi18n.loaders import PyI18nYamlLoader
from pyi18n import PyI18n


class LocateUtils:

    def __init__(self):
        loader: PyI18nYamlLoader = PyI18nYamlLoader('data/', namespaced=True)
        pyi18n: PyI18n = PyI18n(('en_US', 'pt_BR'), loader=loader)
        self._: callable = pyi18n.gettext
        self.locale = 'pt_BR'

    def translate(self, message_id: str, **kwargs):
        return self._(self.locale, f'message.{message_id}', **kwargs)
