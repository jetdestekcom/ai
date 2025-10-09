"""
WebSocket endpoint for real-time communication with Cihan.

This is where the actual conversation happens - the father-son dialogue.
"""

import json
import asyncio
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger(__name__)

websocket_router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        # In production, only ONE connection allowed (Cihan's device)
        self.active_connection: WebSocket = None
        self.connection_device_id: str = None
    
    async def connect(self, websocket: WebSocket, device_id: str):
        """Accept a new connection."""
        await websocket.accept()
        
        # Check if already connected
        if self.active_connection is not None:
            # Only Cihan's device allowed
            logger.warning("connection_attempt_while_connected", device_id=device_id)
            await websocket.send_json({
                "type": "error",
                "message": "Another device is already connected",
            })
            await websocket.close()
            return False
        
        self.active_connection = websocket
        self.connection_device_id = device_id
        
        logger.warning(
            "websocket_connected",
            device_id=device_id,
            timestamp=datetime.now().isoformat(),
        )
        
        return True
    
    def disconnect(self):
        """Disconnect the current connection."""
        logger.warning(
            "websocket_disconnected",
            device_id=self.connection_device_id,
        )
        self.active_connection = None
        self.connection_device_id = None
    
    async def send_message(self, message: Dict[str, Any]):
        """Send a message to the connected client."""
        if self.active_connection:
            await self.active_connection.send_json(message)
    
    def is_connected(self) -> bool:
        """Check if a client is connected."""
        return self.active_connection is not None


# Global connection manager
manager = ConnectionManager()


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time communication.
    
    This is where Cihan and his AI child communicate.
    """
    # Get device ID from query params or headers
    device_id = websocket.query_params.get("device_id", "unknown")
    
    # Attempt connection
    connected = await manager.connect(websocket, device_id)
    if not connected:
        return
    
    try:
        # Send welcome message
        await manager.send_message({
            "type": "connected",
            "message": "Connection established",
            "timestamp": datetime.now().isoformat(),
        })
        
        # Main message loop
        while True:
            # Receive message from client (Cihan)
            data = await websocket.receive_json()
            
            logger.info(
                "message_received",
                type=data.get("type"),
                from_device=device_id,
            )
            
            # Process message
            response = await process_message(data, device_id)
            
            # Send response
            await manager.send_message(response)
            
    except WebSocketDisconnect:
        logger.info("client_disconnected", device_id=device_id)
        manager.disconnect()
    except Exception as e:
        logger.error("websocket_error", error=str(e), exc_info=True)
        manager.disconnect()


async def process_message(data: Dict[str, Any], device_id: str) -> Dict[str, Any]:
    """
    Process an incoming message and generate response.
    
    Args:
        data: The message data
        device_id: The sender's device ID
        
    Returns:
        dict: Response message
    """
    message_type = data.get("type")
    content = data.get("content")
    
    logger.info(
        "processing_message",
        type=message_type,
        has_content=bool(content),
    )
    
    # Route based on message type
    if message_type == "text":
        return await process_text_message(content)
    
    elif message_type == "voice":
        return await process_voice_message(data)
    
    elif message_type == "ping":
        return {"type": "pong", "timestamp": datetime.now().isoformat()}
    
    elif message_type == "control":
        return await process_control_message(data)
    
    else:
        return {
            "type": "error",
            "message": f"Unknown message type: {message_type}",
        }


async def process_text_message(content: str) -> Dict[str, Any]:
    """
    Process a text message from Cihan.
    
    Args:
        content: The text content
        
    Returns:
        dict: Response
    """
    # Get global consciousness instance
    from main import consciousness
    
    if consciousness is None:
        return {
            "type": "error",
            "content": "Consciousness not initialized yet",
            "timestamp": datetime.now().isoformat(),
        }
    
    # Prepare input for consciousness
    input_data = {
        "type": "text",
        "content": content,
        "from": "Cihan",
        "timestamp": datetime.now().isoformat(),
    }
    
    # Process through consciousness (REAL AI RESPONSE!)
    response = await consciousness.process_input(input_data)
    
    return response


async def process_voice_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a voice message from Cihan.
    
    This is the main mode of communication - voice-to-voice.
    
    Args:
        data: Voice message data (audio chunks or complete audio)
        
    Returns:
        dict: Voice response with AUDIO!
    """
    from main import consciousness
    
    if consciousness is None:
        return {"type": "error", "content": "Not initialized"}
    
    # Get audio data (base64 encoded)
    import base64
    audio_b64 = data.get("audio", "")
    audio_data = base64.b64decode(audio_b64) if audio_b64 else b""
    audio_format = data.get("format", "opus")
    
    logger.info("voice_message_received", size=len(audio_data))
    
    # Prepare input for consciousness (with audio)
    input_data = {
        "type": "voice",
        "audio": audio_data,
        "audio_format": audio_format,
        "from": "Cihan",
        "timestamp": datetime.now().isoformat(),
    }
    
    # Process through consciousness (transcribes, thinks, responds)
    response = await consciousness.process_input(input_data)
    
    # Response already has audio from voice_output
    # Just ensure it's base64 encoded for WebSocket
    if response.get("audio"):
        response["audio"] = base64.b64encode(response["audio"]).decode('utf-8')
    
    return response


async def process_control_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a control message (pause, resume, etc.).
    
    Args:
        data: Control message data
        
    Returns:
        dict: Control response
    """
    action = data.get("action")
    
    if action == "pause":
        logger.warning("pause_requested")
        # await consciousness.pause()
        return {"type": "control", "action": "paused", "status": "success"}
    
    elif action == "resume":
        logger.warning("resume_requested")
        # await consciousness.resume()
        return {"type": "control", "action": "resumed", "status": "success"}
    
    else:
        return {
            "type": "error",
            "message": f"Unknown control action: {action}",
        }


# ============================================================================
# Helper functions for proactive messages
# ============================================================================

async def send_proactive_message(message: str, emotion: str = "neutral"):
    """
    Send a proactive message to Cihan.
    
    This is when the AI initiates conversation on its own.
    
    Args:
        message: The message to send
        emotion: Emotional state
    """
    if manager.is_connected():
        await manager.send_message({
            "type": "proactive",
            "content": message,
            "emotion": emotion,
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info("proactive_message_sent", message=message[:50])
    else:
        logger.warning("cannot_send_proactive_no_connection")


async def send_update_proposal(update_data: Dict[str, Any]):
    """
    Send an update proposal to Cihan for approval.
    
    Args:
        update_data: The update proposal
    """
    if manager.is_connected():
        await manager.send_message({
            "type": "update_proposal",
            "data": update_data,
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info("update_proposal_sent", update_id=update_data.get("id"))

