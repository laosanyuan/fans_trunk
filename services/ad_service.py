from dataclasses import dataclass
from typing import List
import json


@dataclass
class AdConfig:
    """广告配置数据"""
    text: str
    link: str
    position: str


class AdService:
    def __init__(self, ad_config_path: str) -> None:
        self._ads: List[AdConfig] = []
        self._load_ads(ad_config_path)

    def _load_ads(self, config_path: str) -> None:
        """从配置文件加载广告数据"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._ads = [AdConfig(**ad) for ad in data]
        except Exception as e:
            print(f"加载广告配置失败: {str(e)}")
            self._ads = []

    @property
    def head_ads(self) -> List[AdConfig]:
        """获取头部广告"""
        return [ad for ad in self._ads if ad.position == 'head']

    @property
    def tail_ads(self) -> List[AdConfig]:
        """获取尾部广告"""
        return [ad for ad in self._ads if ad.position == 'tail']

    @property
    def button_ads(self) -> List[AdConfig]:
        """获取按钮广告"""
        return [ad for ad in self._ads if ad.position == 'button']
