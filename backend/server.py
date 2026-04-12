import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

from room_manager import RoomManager
from game_core import GameCore
import asyncio

rm = RoomManager()

@sio.event
async def connect(sid, environ, auth):
    print(f"User connected: {sid}")
    rm.add_user(sid, f"Guest_{sid[:4]}")
    await sio.emit("info", {"sid": sid, "name": rm.users[sid]["name"]}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"User disconnected: {sid}")
    room_id = rm.leave_room(sid)
    rm.remove_user(sid)
    if room_id:
        if rm.rooms.get(room_id):
            await broadcast_room(room_id)

@sio.event
async def set_name(sid, name):
    if sid in rm.users:
        rm.users[sid]["name"] = name
        await sio.emit("info", {"name": name}, room=sid)

@sio.event
async def create_room(sid):
    room_id = rm.create_room(sid)
    await sio.emit("room_created", {"room_id": room_id}, room=sid)
    await broadcast_room(room_id)
    await broadcast_lobby()

@sio.event
async def join_room(sid, room_id):
    if rm.join_room(sid, room_id):
        await broadcast_room(room_id)
    else:
        await sio.emit("error", {"msg": "Cannot join room"}, room=sid)

@sio.event
async def add_ai(sid):
    ai_sid = rm.add_ai_to_room(sid)
    if ai_sid:
        room_id = rm.users[sid]["room_id"]
        await broadcast_room(room_id)

async def broadcast_room(room_id):
    info = rm.get_room_info(room_id)
    if not info: return
    for p in info["players"]:
        if not p.get("is_ai"):
            await sio.emit("room_update", info, room=p["sid"])

async def broadcast_lobby():
    rooms_data = rm.get_lobby_info()
    await sio.emit("lobby_update", rooms_data)

@sio.event
async def get_lobby(sid):
    rooms_data = rm.get_lobby_info()
    await sio.emit("lobby_update", rooms_data, room=sid)

@sio.event
async def start_game(sid):
    room_id = rm.users[sid]["room_id"]
    if rm.rooms[room_id]["owner"] == sid and len(rm.rooms[room_id]["players"]) == 2:
        p1_sid, p2_sid = rm.rooms[room_id]["players"]
        p1_is_ai = rm.users[p1_sid].get("is_ai", False)
        p2_is_ai = rm.users[p2_sid].get("is_ai", False)
        game = GameCore(p1_sid, rm.users[p1_sid]["name"], p1_is_ai,
                        p2_sid, rm.users[p2_sid]["name"], p2_is_ai)
        rm.rooms[room_id]["game"] = game
        await broadcast_room(room_id)
        await broadcast_game_state(room_id)
        asyncio.create_task(run_ai_if_needed(room_id))

@sio.event
async def play_card(sid, card_idx):
    room_id = rm.users[sid].get("room_id")
    if not room_id or not rm.rooms[room_id].get("game"): return
    game = rm.rooms[room_id]["game"]
    player_idx = 0 if game.players[0].sid == sid else 1
    if game.play_card(player_idx, card_idx):
        await broadcast_game_state(room_id)
        asyncio.create_task(run_ai_if_needed(room_id))

@sio.event
async def choose_match(sid, match_idx):
    room_id = rm.users[sid].get("room_id")
    if not room_id or not rm.rooms[room_id].get("game"): return
    game = rm.rooms[room_id]["game"]
    player_idx = 0 if game.players[0].sid == sid else 1
    if game.choose_match(player_idx, match_idx):
        await broadcast_game_state(room_id)
        asyncio.create_task(run_ai_if_needed(room_id))

@sio.event
async def choose_koikoi(sid, choice):
    room_id = rm.users[sid].get("room_id")
    if not room_id or not rm.rooms[room_id].get("game"): return
    game = rm.rooms[room_id]["game"]
    player_idx = 0 if game.players[0].sid == sid else 1
    if game.choose_koikoi(player_idx, choice):
        await broadcast_game_state(room_id)
        asyncio.create_task(run_ai_if_needed(room_id))

async def broadcast_game_state(room_id):
    game = rm.rooms[room_id]["game"]
    if not game: return
    state = game.get_state()
    for i, p_sid in enumerate(rm.rooms[room_id]["players"]):
        if not rm.users[p_sid].get("is_ai"):
            p_state = state.copy()
            if i == 0:
                p_state["my_player"] = game.players[0].to_dict_with_hand()
                p_state["opp_player"] = game.players[1].to_dict()
                p_state["my_idx"] = 0
            else:
                p_state["my_player"] = game.players[1].to_dict_with_hand()
                p_state["opp_player"] = game.players[0].to_dict()
                p_state["my_idx"] = 1
            await sio.emit("game_state", p_state, room=p_sid)

async def run_ai_if_needed(room_id):
    await asyncio.sleep(1.0)
    game = rm.rooms.get(room_id, {}).get("game")
    if not game or game.state == "GAME_OVER": return
    
    current_actor = game.players[game.current_action_player]
    if current_actor.is_ai:
        if game.state == "WAITING_FOR_PLAY":
            game.play_card(game.current_action_player, 0)
        elif game.state == "WAITING_FOR_MATCH_CHOICE":
            game.choose_match(game.current_action_player, 0)
        elif game.state == "WAITING_FOR_KOIKOI":
            game.choose_koikoi(game.current_action_player, False)
        
        await broadcast_game_state(room_id)
        asyncio.create_task(run_ai_if_needed(room_id))

import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(base_dir, 'frontend')
cards_dir = os.path.join(base_dir, 'cards')

@sio.event
async def leave_room(sid):
    room_id = rm.users.get(sid, {}).get("room_id")
    if room_id:
        rm.leave_room(sid)
        await broadcast_room(room_id)
        await broadcast_lobby()

@sio.event
async def agree_next_round(sid):
    room_id = rm.users[sid].get("room_id")
    if not room_id or not rm.rooms[room_id].get("game"): return
    game = rm.rooms[room_id]["game"]
    
    if not hasattr(game, "agreed_players"):
        game.agreed_players = set()
    game.agreed_players.add(sid)
    
    real_sids = [p for p in rm.rooms[room_id]["players"] if not rm.users[p].get("is_ai")]
    if all(p in game.agreed_players for p in real_sids):
        game.agreed_players.clear()
        game.next_round()
        await broadcast_game_state(room_id)
        asyncio.create_task(run_ai_if_needed(room_id))

@sio.event
async def escape_game(sid):
    room_id = rm.users[sid].get("room_id")
    if room_id and room_id in rm.rooms:
        if rm.rooms[room_id].get("game"):
            rm.rooms[room_id]["game"] = None  # Reset Game
        await broadcast_room(room_id)

app = socketio.ASGIApp(sio, static_files={
    '/': os.path.join(frontend_dir, 'index.html'),
    '/index.css': os.path.join(frontend_dir, 'index.css'),
    '/app.js': os.path.join(frontend_dir, 'app.js'),
    '/cards': cards_dir
})
