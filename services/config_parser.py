import json


class ConfigParser:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def get_bot_token(self):
        return self.config['bot_token']

    def get_admin_user(self):
        return self.config['admin_user']

    def get_proxy(self):
        return self.config['proxy']

    def get_wxpusher_token(self):
        return self.config['wxpusher_token']

    def get_wxpusher_uid(self):
        return self.config['wxpusher_uid']

    def _load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)