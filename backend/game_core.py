# game_core.py
import random
from card import Card
from player import Player

predefined_cps = {
    ("博丽灵梦", "雾雨魔理沙"), ("雾雨魔理沙", "东风谷早苗"), ("博丽灵梦", "东风谷早苗"),
    ("博丽灵梦", "八云紫"), ("蓬莱山辉夜", "藤原妹红"), ("铃仙","八意永琳"),
    ("古明地觉","蕾米莉亚"), ("泄矢诹访子","琪露诺"), ("藤原妹红", "琪露诺"),
}

cp_combinations = {
    "主角组1": {"chars": ["博丽灵梦", "雾雨魔理沙"], "scenes": ["妖怪之山的红叶", "博丽神社的祭典", "幽灵客船之旅", "盛开的樱花树"]},
    "主角组2": {"chars": ["雾雨魔理沙", "东风谷早苗"], "scenes": ["幽灵客船之旅"]},
    "主角组3": {"chars": ["博丽灵梦", "东风谷早苗"], "scenes": ["幽灵客船之旅"]},
    "巫女组": {"chars": ["博丽灵梦", "东风谷早苗"], "scenes": ["妖怪之山的红叶", "博丽神社的祭典"]},
    "守矢组": {"chars": ["泄矢诹访子", "东风谷早苗"], "scenes": ["妖怪之山的红叶"]},
    "白村组": {"chars": ["村纱水蜜", "圣白莲"], "scenes": ["幽灵客船之旅"]},
    "青蛙组": {"chars": ["琪露诺", "泄矢诹访子"], "spots": ["雾之湖"]},
    "八云家组": {"chars": ["橙", "八云蓝", "八云紫"], "scenes": []},
    "幽冥组": {"chars": ["魂魄妖梦", "西行寺幽幽子"], "scenes": ["盛开的樱花树"]},
    "冰火组": {"chars": ["藤原妹红", "琪露诺"], "scenes": ["迷失竹林的月圆之夜"]},
}

yrn_combinations = {
    "结界组": {"chars": ["博丽灵梦", "八云紫"], "scenes": ["迷失竹林的月圆之夜"]},
    "咏唱组": {"chars": ["雾雨魔理沙", "爱丽丝"], "scenes": ["迷失竹林的月圆之夜"]},
    "红魔组": {"chars": ["蕾米莉亚", "十六夜咲夜"], "scenes": ["迷失竹林的月圆之夜"]},
    "幽冥组": {"chars": ["魂魄妖梦", "西行寺幽幽子"], "scenes": ["迷失竹林的月圆之夜"]},
    "永远组": {"chars": ["八意永琳", "蓬莱山辉夜"], "scenes": ["迷失竹林的月圆之夜"]},
    "不死组": {"chars": ["蓬莱山辉夜", "藤原妹红"], "scenes": ["迷失竹林的月圆之夜"]}
}

def check_cp_combinations(collected_cards):
    char_set = set(c.name for c in collected_cards if c.card_type == 'character')
    scene_set = set(c.name for c in collected_cards if c.card_type == 'scene')
    spot_set = set(c.name for c in collected_cards if c.card_type == 'spot')

    yizhong_cp = []
    cp_count = 0

    for combo_name, combo in cp_combinations.items():
        if not all(char in char_set for char in combo["chars"]):
            continue
        if "scenes" in combo and combo["scenes"] and not any(scene in scene_set for scene in combo["scenes"]):
            continue
        if "spots" in combo and combo["spots"] and not any(spot in spot_set for spot in combo["spots"]):
            continue
        cp_count += 1
        yizhong_cp.append(combo_name)

    for combo_name, combo in yrn_combinations.items():
        if not all(char in char_set for char in combo["chars"]):
            continue
        if "scenes" in combo and combo["scenes"] and not any(scene in scene_set for scene in combo["scenes"]):
            continue
        cp_count += 1
        yizhong_cp.append('永夜组')
        break  # 只需满足一个永夜组组合
    return cp_count, yizhong_cp

def calculate_score(player, ids):
    collected = player.collected
    total_score = 0
    rm = False
    yizhong = []
    
    scene_names = [c.name for c in collected if c.card_type == 'scene']
    item_names = [c.name for c in collected if c.card_type == 'item']
    spot_names = [c.name for c in collected if c.card_type == 'spot']
    char_names = [c.name for c in collected if c.card_type == 'character']
    yyc_chars = ["博丽灵梦", "八云紫", "雾雨魔理沙", "爱丽丝", "蕾米莉亚", "十六夜咲夜", "西行寺幽幽子", "魂魄妖梦" ]
    
    if len(scene_names) == 5:
        total_score += 10
        yizhong.append("五景")
    elif "迷失竹林的月圆之夜" in scene_names:
        if not any(c in char_names for c in yyc_chars):
            rm = True
            scene_names.remove("迷失竹林的月圆之夜")
            
    if len(scene_names) >= 3 and len(scene_names) != 5:
        if len(scene_names) == 4:
            total_score += 8
            yizhong.append("四景")
        if len(scene_names) == 3:
            total_score += 5
            yizhong.append("三景")
            
    if rm:
        scene_names.append("迷失竹林的月圆之夜")
        
    cp_count, yizhong_cp = check_cp_combinations(collected)
    yizhong += yizhong_cp
    total_score += cp_count * 3
    
    if ids != []:
        list2 = [0]*12
        for item in collected:
            list2[item.card_id-1] += 1
        for hezha in ids:
            if list2[hezha-1] == 4:
                total_score += 4
                for hespcard in collected:
                    if hespcard.card_id == hezha and hespcard.card_type == 'spot':
                        yizhong.append(f"合札{hespcard.name}")
                        
    weapon_items = ["灵梦的御币", "早苗的御币", "楼观剑和白楼剑"]
    if all(item in item_names for item in weapon_items):
        total_score += 5
        yizhong.append("武器库")
        
    faith_spots = ["博丽神社", "守矢神社", "命莲寺"]
    if all(spot in spot_names for spot in faith_spots):
        total_score += 5
        yizhong.append("信仰战争")
        if "巫女组" in yizhong:
            yizhong.remove("巫女组")
            
    item_count = len(item_names)
    if item_count >= 5:
        total_score += item_count - 5 + 1
        yizhong.append(f"物品牌{item_count}张")
        
    spot_count = len(spot_names)
    if spot_count >= 5:
        total_score += spot_count - 5 + 1
        yizhong.append(f"地点牌{spot_count}张")
        
    char_count = len(char_names)
    if char_count >= 10:
        total_score += char_count - 10 + 1
        yizhong.append(f"人物牌{char_count}张")
        
    # Check if new yizhong is obtained
    if yizhong != player.yizhong and yizhong != []: # Wait, if any score is >0 or new yizhong obtained
        new_yizhong = True
    else:
        new_yizhong = False
        
    return total_score, yizhong, new_yizhong

"""
state machine statuses:
- WAITING_FOR_PLAY: next player selects a card from hand to play
- WAITING_FOR_DISCARD_MATCH: player played card, 2 matches on field, player must choose 1
- WAITING_FOR_DRAW_MATCH: deck card drawn, 2 matches, player must choose 1
- WAITING_FOR_KOIKOI: player got new yizhong, must decide whether to continue(koikoi) or end
- GAME_OVER: round ended
"""

class GameCore:
    def __init__(self, p1_sid, p1_name, p1_is_ai, p2_sid, p2_name, p2_is_ai):
        self.players = [
            Player(p1_name, p1_sid, p1_is_ai),
            Player(p2_name, p2_sid, p2_is_ai)
        ]
        self.deck = Card.initialize_cards()
        random.shuffle(self.deck)
        
        self.players[0].initial_draw(self.deck)
        self.players[1].initial_draw(self.deck)
        self.field = self.deck[:8]
        self.deck = self.deck[8:]
        self.spot_ids_at_start = [int(v.card_id) for v in self.field if v.card_type == 'spot']
        
        self.current_turn = 0 # 0 or 1
        self.state = "WAITING_FOR_PLAY"
        
        # Temporary states
        self.pending_played_card = None
        self.pending_drawn_card = None
        self.pending_matches = []
        self.current_action_player = 0 # Who is required to make the current choice
        
        # Check initial tianhu / flow here if needed, but skipped for simplicity
        
    def get_current_player(self):
        return self.players[self.current_turn]
        
    def get_state(self):
        return {
            "p1": self.players[0].to_dict(),
            "p2": self.players[1].to_dict(),
            "field": [c.to_dict() for c in self.field],
            "deck_count": len(self.deck),
            "state": self.state,
            "current_turn_sid": self.players[self.current_turn].sid,
            "current_action_sid": self.players[self.current_action_player].sid,
            "pending_matches": [c.to_dict() for c in self.pending_matches] if hasattr(self, 'pending_matches') else []
        }

    def play_card(self, player_idx, card_idx):
        if self.state != "WAITING_FOR_PLAY" or self.current_turn != player_idx:
            return False
            
        player = self.players[player_idx]
        if card_idx < 0 or card_idx >= len(player.hand):
            return False
            
        card = player.hand.pop(card_idx)
        return self._process_played_card(player, card, is_from_deck=False)
        
    def _process_played_card(self, player, card, is_from_deck=False):
        matched_cards = [c for c in self.field if c.card_id == card.card_id]
        
        if not matched_cards:
            self.field.append(card)
            return self._proceed_after_play(is_from_deck)
            
        if len(matched_cards) == 1:
            player.collected.append(card)
            player.collected.append(matched_cards[0])
            self.field.remove(matched_cards[0])
            return self._proceed_after_play(is_from_deck)
            
        if len(matched_cards) >= 3: # 4 cards total, auto collect all
            player.collected.append(card)
            for m in matched_cards:
                player.collected.append(m)
                self.field.remove(m)
            return self._proceed_after_play(is_from_deck)

        # 2 matches! Need user choice
        self.pending_played_card = card
        self.pending_matches = matched_cards
        self.pending_is_deck = is_from_deck
        self.current_action_player = self.current_turn
        self.state = "WAITING_FOR_MATCH_CHOICE"
        return True

    def _proceed_after_play(self, was_from_deck):
        if was_from_deck:
            player = self.players[self.current_turn]
            round_score, yizhong, new_yizhong = calculate_score(player, self.spot_ids_at_start)
            player.round_score = round_score
            player.yizhong = yizhong
            if new_yizhong:
                self.state = "WAITING_FOR_KOIKOI"
                self.current_action_player = self.current_turn
                return True
            else:
                return self._next_turn()
        else:
            # Now draw a card from deck
            if not self.deck:
                return self._next_turn()
            drawn_card = self.deck.pop(0)
            return self._process_played_card(self.players[self.current_turn], drawn_card, is_from_deck=True)

    def choose_match(self, player_idx, match_idx):
        if self.state != "WAITING_FOR_MATCH_CHOICE" or self.current_action_player != player_idx:
            return False
            
        player = self.players[player_idx]
        chosen = self.pending_matches[match_idx]
        player.collected.append(self.pending_played_card)
        player.collected.append(chosen)
        self.field.remove(chosen)
        
        # Clear pending
        is_deck = self.pending_is_deck
        self.pending_played_card = None
        self.pending_matches = []
        return self._proceed_after_play(is_deck)

    def choose_koikoi(self, player_idx, koikoi):
        if self.state != "WAITING_FOR_KOIKOI" or self.current_action_player != player_idx:
            return False
            
        player = self.players[player_idx]
        
        if not koikoi: # 结束
            player.score += player.round_score
            opponent = self.players[1 - player_idx]
            opponent.round_score = 0
            opponent.yizhong = []
            
            self.state = "GAME_OVER"
        else:
            self._next_turn()
        return True

    def _next_turn(self):
        if not self.players[0].hand and not self.players[1].hand:
            self.players[0].round_score = 0
            self.players[1].round_score = 0
            self.state = "GAME_OVER"
            return True
            
        self.current_turn = 1 - self.current_turn
        self.current_action_player = self.current_turn
        self.state = "WAITING_FOR_PLAY"
        return True

    def next_round(self):
        self.deck = Card.initialize_cards()
        random.shuffle(self.deck)
        for p in self.players:
            p.hand = []
            p.collected = []
            p.yizhong = []
            p.round_score = 0
            p.initial_draw(self.deck)
        self.field = self.deck[:8]
        self.deck = self.deck[8:]
        self.spot_ids_at_start = [int(v.card_id) for v in self.field if v.card_type == 'spot']
        
        self.current_turn = 1 - self.current_turn
        self.current_action_player = self.current_turn
        self.state = "WAITING_FOR_PLAY"
        self.pending_played_card = None
        self.pending_matches = []
        return True
