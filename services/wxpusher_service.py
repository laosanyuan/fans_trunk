import inject
import requests

from services.config_parser import ConfigParser


class WxPusherService():
    @inject.autoparams()
    def __init__(self, config_parser: ConfigParser) -> None:
        self.token = config_parser.get_wxpusher_token()
        self.uid = config_parser.get_wxpusher_uid()

    def push(self, title: str, content: str):
        webapi = 'http://wxpusher.zjiecode.com/api/send/message'
        data = {
            "appToken": self.token,
            "content": content,
            "summary": title,
            "contentType": 1,
            "uids": [self.uid, ],
        }
        result = requests.post(url=webapi, json=data)
        return result.status_code == 200
