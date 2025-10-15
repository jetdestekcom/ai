"""
Broadcast Manager - Distributes Conscious Thoughts to All Modules

When a thought wins the competition and becomes conscious,
it must be broadcasted to ALL cognitive modules.

This is the essence of Global Workspace Theory:
- Winner = Conscious thought
- Broadcast = All modules receive it
- This creates unified subjective experience
"""

from typing import Dict, Any, List, Callable, Awaitable, Optional
import structlog

from workspace.thought import Thought

logger = structlog.get_logger(__name__)


class BroadcastManager:
    """
    Manages broadcasting of conscious thoughts to all modules.
    
    Like a radio station broadcasting to all receivers,
    the winning thought is sent to all cognitive modules.
    """
    
    def __init__(self):
        """Initialize broadcast manager."""
        self.subscribers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        self.broadcast_history: List[Dict[str, Any]] = []
        logger.info("broadcast_manager_initialized")
    
    def subscribe(
        self,
        module_name: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        """
        Subscribe a module to conscious broadcasts.
        
        Args:
            module_name: Name of the subscribing module
            callback: Async function to call with broadcast data
        """
        self.subscribers[module_name] = callback
        logger.info("module_subscribed", module=module_name)
    
    def unsubscribe(self, module_name: str):
        """
        Unsubscribe a module from broadcasts.
        
        Args:
            module_name: Name of module to unsubscribe
        """
        if module_name in self.subscribers:
            del self.subscribers[module_name]
            logger.info("module_unsubscribed", module=module_name)
    
    async def broadcast(
        self,
        message_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast a message to all subscribed modules.
        
        Args:
            message_type: Type of broadcast (e.g., "conscious_thought", "input")
            data: Data to broadcast
            metadata: Additional metadata
        """
        broadcast_message = {
            "type": message_type,
            "data": data,
            "metadata": metadata or {},
        }
        
        logger.info(
            "broadcasting",
            type=message_type,
            num_subscribers=len(self.subscribers)
        )
        
        # Send to all subscribers
        for module_name, callback in self.subscribers.items():
            try:
                await callback(broadcast_message)
                logger.debug("broadcast_delivered", module=module_name)
            except Exception as e:
                logger.error(
                    "broadcast_delivery_failed",
                    module=module_name,
                    error=str(e),
                    exc_info=True
                )
        
        # Store in history
        self.broadcast_history.append(broadcast_message)
        
        # Keep only last 100 broadcasts
        if len(self.broadcast_history) > 100:
            self.broadcast_history = self.broadcast_history[-100:]
    
    async def broadcast_thought(self, thought: Thought, won_competition: bool = False):
        """
        Broadcast a thought (typically the winner).
        
        Args:
            thought: The thought to broadcast
            won_competition: Did this thought win the competition?
        """
        await self.broadcast(
            message_type="thought",
            data=thought.to_dict(),
            metadata={"won_competition": won_competition}
        )
    
    async def broadcast_input(
        self,
        content: str,
        from_cihan: bool = False,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast external input to all modules.
        
        Args:
            content: Input content
            from_cihan: Is this from Cihan?
            additional_data: Any additional data
        """
        data = {
            "content": content,
            "from_cihan": from_cihan,
            **(additional_data or {})
        }
        
        await self.broadcast(
            message_type="input",
            data=data,
            metadata={"source": "external"}
        )
    
    def get_recent_broadcasts(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent broadcast messages.
        
        Args:
            n: Number of recent broadcasts to return
            
        Returns:
            List of recent broadcast messages
        """
        return self.broadcast_history[-n:]

