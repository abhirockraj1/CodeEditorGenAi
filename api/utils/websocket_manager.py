from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}  # {file_id: {user_id: WebSocket}}

    async def connect(self, websocket: WebSocket, file_id: int, user_id: int):
        await websocket.accept()
        if file_id not in self.active_connections:
            self.active_connections[file_id] = {}
        self.active_connections[file_id][user_id] = websocket

    def disconnect(self, file_id: int, user_id: int):
        if file_id in self.active_connections and user_id in self.active_connections[file_id]:
            del self.active_connections[file_id][user_id]
            if not self.active_connections[file_id]:
                del self.active_connections[file_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, file_id: int, exclude_user_id: int = None):
        if file_id in self.active_connections:
            for user_id, connection in self.active_connections[file_id].items():
                if user_id != exclude_user_id:
                    await connection.send_json(message)

manager = WebSocketManager()