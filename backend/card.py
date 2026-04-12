# card.py

card_types = ('scene', 'item', 'spot', 'character')

class Card:
    def __init__(self, name, card_type, card_id):
        self.name = name
        self.card_type = card_type
        self.card_id = card_id
        
    def to_dict(self):
        return {
            "name": self.name,
            "card_type": self.card_type,
            "card_id": self.card_id,
            "img_url": f"/cards/{self.name}.png"
        }

    @staticmethod
    def initialize_cards():
        card_list = [
            # 景色牌 (scene) - 共5张
            Card("博丽神社的祭典", "scene", 1),
            Card("迷失竹林的月圆之夜", "scene", 2),
            Card("妖怪之山的红叶", "scene", 4),
            Card("幽灵客船之旅", "scene", 8),
            Card("盛开的樱花树", "scene", 11),

            # 物品牌 (item) - 共9张
            Card("灵梦的御币", "item", 1),
            Card("早苗的御币", "item", 3),
            Card("隙间", "item", 5),
            Card("小石子帽子", "item", 6),
            Card("国士无双之药", "item", 7),
            Card("致幻蘑菇", "item", 9),
            Card("魔导书", "item", 10),
            Card("楼观剑和白楼剑", "item", 11),
            Card("琪露诺的战书", "item", 12),

            # 地点牌 (spot) - 共10张
            Card("博丽神社", "spot", 1),
            Card("迷失竹林", "spot", 2),
            Card("守矢神社", "spot", 3),
            Card("妖怪之山", "spot", 4),
            Card("地灵殿", "spot", 6),
            Card("永远亭", "spot", 7),
            Card("命莲寺", "spot", 8),
            Card("魔法森林", "spot", 9),
            Card("红魔馆", "spot", 10),
            Card("雾之湖", "spot", 12),

            # 人物牌 (character) - 共24张
            Card("博丽灵梦", "character", 1),
            Card("藤原妹红", "character", 2),
            Card("铃仙", "character", 2),
            Card("东风谷早苗", "character", 3),
            Card("泄矢诹访子", "character", 3),
            Card("射命丸文", "character", 4),
            Card("键山雏", "character", 4),
            Card("橙", "character", 5),
            Card("八云蓝", "character", 5),
            Card("八云紫", "character", 5),
            Card("古明地恋", "character", 6),
            Card("古明地觉", "character", 6),
            Card("八意永琳", "character", 7),
            Card("蓬莱山辉夜", "character", 7),
            Card("圣白莲", "character", 8),
            Card("村纱水蜜", "character", 8),
            Card("爱丽丝", "character", 9),
            Card("雾雨魔理沙", "character", 9),
            Card("蕾米莉亚", "character", 10),
            Card("十六夜咲夜", "character", 10),
            Card("魂魄妖梦", "character", 11),
            Card("西行寺幽幽子", "character", 11),
            Card("琪露诺", "character", 12),
            Card("大妖精", "character", 12)
        ]
        return card_list
