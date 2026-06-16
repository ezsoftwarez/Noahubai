"""
Event Bus - Pub/Sub system for agent communication (DETACHED agents)
"""
import asyncio
import logging
from typing import Callable, Dict, List, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event object"""
    name: str
    data: Dict
    timestamp: datetime
    source_agent_id: str = None


class EventBus:
    """
    Publish/Subscribe event bus for decoupled agent communication.
    Agents emit events and subscribe to events without direct coupling.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._lock = asyncio.Lock()
    
    async def subscribe(self, event_name: str, callback: Callable) -> str:
        """
        Subscribe to an event
        
        Args:
            event_name: Event name pattern (supports wildcards like "agent.*")
            callback: Async callable to invoke when event is published
            
        Returns:
            Subscription ID
        """
        async with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            self._subscribers[event_name].append(callback)
            logger.debug(f"Subscribed to event: {event_name}")
        
        return f"{event_name}:{id(callback)}"
    
    async def unsubscribe(self, event_name: str, callback: Callable) -> bool:
        """
        Unsubscribe from an event
        
        Returns:
            True if unsubscribed, False if not found
        """
        async with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(callback)
                    logger.debug(f"Unsubscribed from event: {event_name}")
                    return True
                except ValueError:
                    return False
        return False
    
    async def publish(self, event_name: str, data: Dict = None, source_agent_id: str = None) -> None:
        """
        Publish an event
        
        Args:
            event_name: Event name
            data: Event data
            source_agent_id: ID of agent publishing the event
        """
        if data is None:
            data = {}
        
        event = Event(
            name=event_name,
            data=data,
            timestamp=datetime.utcnow(),
            source_agent_id=source_agent_id
        )
        
        # Store in history
        async with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        logger.debug(f"Published event: {event_name}")
        
        # Find matching subscribers
        matching_callbacks = []
        async with self._lock:
            # Exact match
            if event_name in self._subscribers:
                matching_callbacks.extend(self._subscribers[event_name])
            
            # Wildcard patterns
            for pattern, callbacks in self._subscribers.items():
                if pattern.endswith("*"):
                    prefix = pattern[:-1]
                    if event_name.startswith(prefix):
                        matching_callbacks.extend(callbacks)
        
        # Invoke callbacks concurrently
        if matching_callbacks:
            tasks = [
                self._invoke_callback(callback, event)
                for callback in matching_callbacks
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _invoke_callback(self, callback: Callable, event: Event) -> None:
        """Safely invoke a callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            logger.error(f"Error invoking callback for event {event.name}: {e}", exc_info=True)
    
    async def get_history(self, event_name: str = None, limit: int = 100) -> List[Event]:
        """
        Get event history
        
        Args:
            event_name: Optional filter by event name
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        async with self._lock:
            events = self._event_history[-limit:]
            
            if event_name:
                events = [e for e in events if event_name in e.name]
            
            return events
    
    async def clear_history(self) -> None:
        """Clear event history"""
        async with self._lock:
            self._event_history.clear()
    
    def get_subscriptions(self) -> Dict[str, int]:
        """Get subscription counts per event"""
        return {
            event_name: len(callbacks)
            for event_name, callbacks in self._subscribers.items()
            if callbacks
        }
