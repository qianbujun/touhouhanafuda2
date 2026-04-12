# room_manager.py
import uuid
from typing import Dict, List

class RoomManager:
    def __init__(self):
        self.rooms = {}  # room_id -> {"players": [], "game": GameCore/None, "owner": sid}
        self.users = {}  # sid -> {"name": str, "room_id": str}

    def add_user(self, sid, name):
        self.users[sid] = {"name": name, "room_id": None}

    def remove_user(self, sid):
        if sid in self.users:
            room_id = self.users[sid]["room_id"]
            if room_id:
                self.leave_room(sid)
            del self.users[sid]

    def create_room(self, sid):
        room_id = str(uuid.uuid4())[:6].upper()
        self.rooms[room_id] = {
            "players": [sid],
            "game": None,
            "owner": sid
        }
        self.users[sid]["room_id"] = room_id
        return room_id

    def join_room(self, sid, room_id):
        if room_id in self.rooms and len(self.rooms[room_id]["players"]) < 2:
            self.rooms[room_id]["players"].append(sid)
            self.users[sid]["room_id"] = room_id
            return True
        return False

    def leave_room(self, sid):
        room_id = self.users[sid].get("room_id")
        if room_id and room_id in self.rooms:
            self.rooms[room_id]["players"].remove(sid)
            self.users[sid]["room_id"] = None
            # Check if any human player remains
            real_players = [p for p in self.rooms[room_id]["players"] if not self.users.get(p, {}).get("is_ai")]
            if not real_players:
                # Remove AI placeholders
                for p in list(self.rooms[room_id]["players"]):
                    if self.users.get(p, {}).get("is_ai"):
                        del self.users[p]
                del self.rooms[room_id]  # Room empty of humans, delete
            elif self.rooms[room_id]["owner"] == sid:
                # pass ownership to another real player
                self.rooms[room_id]["owner"] = real_players[0]
            return room_id
        return None

    def add_ai_to_room(self, owner_sid):
        room_id = self.users[owner_sid].get("room_id")
        if room_id and self.rooms[room_id]["owner"] == owner_sid:
            if len(self.rooms[room_id]["players"]) < 2:
                ai_sid = f"AI_{uuid.uuid4().hex[:6]}"
                self.users[ai_sid] = {"name": "BAKA(电脑)", "room_id": room_id, "is_ai": True}
                self.rooms[room_id]["players"].append(ai_sid)
                return ai_sid
        return None

    def get_room_info(self, room_id):
        if room_id not in self.rooms: return None
        players = []
        for p_sid in self.rooms[room_id]["players"]:
            players.append({"sid": p_sid, "name": self.users[p_sid]["name"], "is_ai": self.users[p_sid].get("is_ai", False)})
        return {
            "room_id": room_id,
            "owner": self.rooms[room_id]["owner"],
            "players": players,
            "status": "playing" if self.rooms[room_id]["game"] else "waiting"
        }

    def get_lobby_info(self):
        result = []
        for r_id, r_info in self.rooms.items():
            result.append({
                "room_id": r_id,
                "players_count": len(r_info["players"]),
                "status": "playing" if r_info["game"] else "waiting"
            })
        return result
