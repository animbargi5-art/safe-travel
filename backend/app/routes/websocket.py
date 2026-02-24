"""
WebSocket routes for real-time notifications
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database_dep import get_db
from app.services.notification_service import (
    connection_manager, 
    NotificationService, 
    NotificationType, 
    NotificationPriority
)
from app.services.auth_service import verify_token
from app.models.user import User

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

async def get_user_from_token(token: str, db: Session) -> User:
    """Authenticate user from WebSocket token"""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token required")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

@router.websocket("/notifications/{token}")
async def websocket_notifications(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time notifications"""
    
    try:
        # Authenticate user
        user = await get_user_from_token(token, db)
        
        # Connect to notification system
        await connection_manager.connect(websocket, user.id, {
            'user_email': user.email,
            'user_name': user.full_name
        })
        
        # Send initial status
        await connection_manager.send_personal_message({
            'type': 'status',
            'message': f'Welcome {user.full_name}! You are now connected to real-time notifications.',
            'connected_users': connection_manager.get_connection_count(),
            'timestamp': connection_manager.connection_metadata[websocket]['connected_at'].isoformat()
        }, user.id)
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(websocket, user, message, db)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Internal server error'
                }))
                
    except HTTPException as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=e.detail)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error")
    finally:
        connection_manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, user: User, message: Dict[str, Any], db: Session):
    """Handle incoming WebSocket messages from clients"""
    
    message_type = message.get('type')
    
    if message_type == 'ping':
        # Respond to ping with pong
        await websocket.send_text(json.dumps({
            'type': 'pong',
            'timestamp': message.get('timestamp')
        }))
        
    elif message_type == 'subscribe':
        # Subscribe to specific notification types
        subscription_types = message.get('notification_types', [])
        await websocket.send_text(json.dumps({
            'type': 'subscription_confirmed',
            'subscribed_to': subscription_types,
            'message': f'Subscribed to {len(subscription_types)} notification types'
        }))
        
    elif message_type == 'get_status':
        # Send current connection status
        await websocket.send_text(json.dumps({
            'type': 'status_response',
            'user_id': user.id,
            'connected_at': connection_manager.connection_metadata[websocket]['connected_at'].isoformat(),
            'total_connections': connection_manager.get_connection_count(),
            'connected_users': len(connection_manager.get_connected_users())
        }))
        
    elif message_type == 'test_notification':
        # Send test notification (for development/testing)
        notification_service = NotificationService(db)
        await notification_service.create_notification(
            user_id=user.id,
            notification_type=NotificationType.SYSTEM_MAINTENANCE,
            title="Test Notification 🧪",
            message="This is a test notification to verify WebSocket connectivity.",
            priority=NotificationPriority.LOW,
            data={'test': True}
        )
        
    else:
        await websocket.send_text(json.dumps({
            'type': 'error',
            'message': f'Unknown message type: {message_type}'
        }))

# REST endpoints for notification management
@router.get("/connections/stats")
async def get_connection_stats():
    """Get WebSocket connection statistics"""
    return {
        'total_connections': connection_manager.get_connection_count(),
        'connected_users': len(connection_manager.get_connected_users()),
        'user_ids': connection_manager.get_connected_users()
    }

@router.post("/broadcast")
async def broadcast_notification(
    notification_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Broadcast notification to all connected users (admin only)"""
    # In production, add proper admin authentication
    
    notification_service = NotificationService(db)
    
    await connection_manager.broadcast_message({
        'type': 'notification',
        'notification_type': 'system_announcement',
        'title': notification_data.get('title', 'System Announcement'),
        'message': notification_data.get('message', ''),
        'priority': notification_data.get('priority', 'medium'),
        'data': notification_data.get('data', {}),
        'timestamp': notification_data.get('timestamp')
    })
    
    return {
        'status': 'broadcasted',
        'recipients': connection_manager.get_connection_count(),
        'message': 'Notification sent to all connected users'
    }

@router.post("/send/{user_id}")
async def send_notification_to_user(
    user_id: int,
    notification_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Send notification to specific user"""
    # In production, add proper authentication and authorization
    
    notification_service = NotificationService(db)
    
    await notification_service.create_notification(
        user_id=user_id,
        notification_type=NotificationType(notification_data.get('type', 'system_maintenance')),
        title=notification_data.get('title', 'Notification'),
        message=notification_data.get('message', ''),
        priority=NotificationPriority(notification_data.get('priority', 'medium')),
        data=notification_data.get('data', {})
    )
    
    return {
        'status': 'sent',
        'user_id': user_id,
        'message': 'Notification sent successfully'
    }

@router.post("/test/{user_id}")
async def send_test_notification(user_id: int, db: Session = Depends(get_db)):
    """Send test notification to user"""
    notification_service = NotificationService(db)
    
    await notification_service.create_notification(
        user_id=user_id,
        notification_type=NotificationType.SYSTEM_MAINTENANCE,
        title="Test Notification 🧪",
        message="This is a test notification from the Safe Travel system.",
        priority=NotificationPriority.LOW,
        data={'test': True, 'sent_at': 'now'}
    )
    
    return {
        'status': 'test_sent',
        'user_id': user_id,
        'message': 'Test notification sent'
    }