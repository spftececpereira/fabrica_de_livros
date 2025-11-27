from typing import Dict, Set
import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import User
from app.api.deps import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        # user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.notification_service = NotificationService()

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected_connections = set()
            for connection in self.active_connections[user_id].copy():
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Connection is broken, mark for removal
                    disconnected_connections.add(connection)
            
            # Remove broken connections
            for connection in disconnected_connections:
                self.active_connections[user_id].discard(connection)

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        disconnected_connections = []
        
        for user_id, connections in self.active_connections.items():
            for connection in connections.copy():
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected_connections.append((user_id, connection))
        
        # Clean up broken connections
        for user_id, connection in disconnected_connections:
            self.disconnect(connection, user_id)

    async def send_book_generation_update(
        self, 
        user_id: int, 
        book_id: int, 
        task_id: str, 
        status: str, 
        progress: int, 
        message: str,
        current_step: str = None
    ):
        """Send book generation status update"""
        notification = {
            "type": "book_generation_update",
            "timestamp": asyncio.get_event_loop().time(),
            "data": {
                "book_id": book_id,
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "message": message,
                "current_step": current_step
            }
        }
        await self.send_personal_message(notification, user_id)

    async def send_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info",
        action_url: str = None
    ):
        """Send general notification"""
        notification = {
            "type": "notification",
            "timestamp": asyncio.get_event_loop().time(),
            "data": {
                "id": f"notif_{asyncio.get_event_loop().time()}",
                "title": title,
                "message": message,
                "type": notification_type,
                "action_url": action_url
            }
        }
        await self.send_personal_message(notification, user_id)

    def get_connected_users(self) -> Set[int]:
        """Get list of currently connected user IDs"""
        return set(self.active_connections.keys())

    def is_user_connected(self, user_id: int) -> bool:
        """Check if user is currently connected"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

# Global connection manager instance
manager = ConnectionManager()

# WebSocket authentication
async def get_websocket_user(websocket: WebSocket) -> User:
    """Authenticate WebSocket connection using token from query params"""
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            raise HTTPException(status_code=401, detail="Missing authentication token")

        # Verify JWT token
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id: int = payload.get("sub")
            if user_id is None:
                await websocket.close(code=4001, reason="Invalid token")
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            await websocket.close(code=4001, reason="Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")

        # Here you would normally get the user from database
        # For now, we'll create a minimal user object
        # In real implementation, you'd do: user = await get_user_by_id(user_id)
        
        class MockUser:
            def __init__(self, user_id: int):
                self.id = user_id
        
        return MockUser(user_id)
        
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        raise

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time notifications"""
    user = None
    try:
        # Authenticate user
        user = await get_websocket_user(websocket)
        
        # Connect user
        await manager.connect(websocket, user.id)
        
        # Send welcome message
        welcome_message = {
            "type": "connection_established",
            "timestamp": asyncio.get_event_loop().time(),
            "data": {
                "message": "Conectado ao sistema de notificações em tempo real",
                "user_id": user.id
            }
        }
        await websocket.send_text(json.dumps(welcome_message))

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (ping/pong, etc.)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Parse client message
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    if message_type == "ping":
                        # Respond to ping
                        pong_message = {
                            "type": "pong",
                            "timestamp": asyncio.get_event_loop().time()
                        }
                        await websocket.send_text(json.dumps(pong_message))
                        
                    elif message_type == "subscribe_book_updates":
                        # Subscribe to specific book updates
                        book_id = message.get("book_id")
                        if book_id:
                            # Store subscription (implement as needed)
                            logger.info(f"User {user.id} subscribed to book {book_id} updates")
                            
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from user {user.id}")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                ping_message = {
                    "type": "ping",
                    "timestamp": asyncio.get_event_loop().time()
                }
                await websocket.send_text(json.dumps(ping_message))
                
    except WebSocketDisconnect:
        if user:
            manager.disconnect(websocket, user.id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user:
            manager.disconnect(websocket, user.id)

# Helper functions for other parts of the application
def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return manager

# API endpoint to send test notifications
@router.post("/notifications/test")
async def send_test_notification(
    user_id: int,
    title: str = "Notificação de Teste",
    message: str = "Esta é uma notificação de teste",
    notification_type: str = "info",
    current_user: User = Depends(get_current_user)
):
    """Send a test notification to specific user (admin only)"""
    # Only admin users can send test notifications
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await manager.send_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type
    )
    
    return {"message": f"Test notification sent to user {user_id}"}

@router.get("/notifications/status")
async def get_notification_status(current_user: User = Depends(get_current_user)):
    """Get WebSocket connection status"""
    connected_users = manager.get_connected_users()
    is_connected = manager.is_user_connected(current_user.id)
    
    return {
        "user_connected": is_connected,
        "total_connected_users": len(connected_users),
        "websocket_endpoint": "/api/v1/websocket/ws"
    }