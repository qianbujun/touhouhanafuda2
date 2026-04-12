# player.py
from card import Card

class Player:
    def __init__(self, name, sid, is_ai=False):
        self.name = name          # 玩家名称
        self.sid = sid            # session id, AI players can have sid="AI-xxx"
        self.is_ai = is_ai
        self.hand = []            # 手牌
        self.collected = []       # 收集的牌
        self.score = 0            # 累计积分
        self.round_score = 0      # 本局积分
        self.yizhong = []         # 达成的役种
        
    def draw(self, deck, num=8):
        """从牌堆抽取指定数量的牌"""
        for _ in range(num):
            if deck:
                self.hand.append(deck.pop(0))
    
    def initial_draw(self, deck):
        """初始发牌：抽取8张手牌"""
        self.draw(deck, 8)
    
    def discard(self, card_index, field):
        """打出指定索引的手牌到场上，由于是Web，直接根据索引移除并返回该牌，不再打印"""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            field.append(card)
            return card
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "sid": self.sid,
            "is_ai": self.is_ai,
            "hand_count": len(self.hand),
            "hand": [c.to_dict() for c in self.hand],
            "collected": [c.to_dict() for c in self.collected],
            "score": self.score,
            "round_score": self.round_score,
            "yizhong": self.yizhong
        }
    
    def to_dict_with_hand(self):
        d = self.to_dict()
        return d
