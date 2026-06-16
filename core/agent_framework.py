"""
Agent framework primitives used by all Noahubai agents.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Lifecycle states for an agent."""

    IDLE = "idle"
    STARTING = "starting"
    READY = "ready"
    WORKING = "working"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


class AgentPriority(str, Enum):
    """Execution priority for an agent."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentConfig:
    """Static configuration for an agent."""

    name: str
    agent_type: str
    description: str
    priority: AgentPriority = AgentPriority.NORMAL
    timeout_seconds: int = 30
    tags: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of invoking an agent task."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseAgent:
    """Base class for detached Noahubai agents."""

    def __init__(self, config: AgentConfig, event_bus, state_manager):
        self.config = config
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.state = AgentState.IDLE
        self.started_at: Optional[datetime] = None
        self.last_error: Optional[str] = None

    async def initialize(self) -> bool:
        """Initialize the agent."""
        if self.state in (AgentState.STARTING, AgentState.READY):
            return True

        self.state = AgentState.STARTING
        try:
            await self._initialize()
            self.started_at = datetime.utcnow()
            self.last_error = None
            self.state = AgentState.READY
            await self._publish_event("agent.ready", {"agent": self.config.name})
            return True
        except Exception as exc:  # pragma: no cover - defensive
            self.last_error = str(exc)
            self.state = AgentState.ERROR
            logger.error("Agent %s failed to initialize: %s", self.config.name, exc, exc_info=True)
            await self._publish_event("agent.error", {"agent": self.config.name, "error": str(exc)})
            return False

    async def shutdown(self) -> None:
        """Shutdown the agent gracefully."""
        if self.state in (AgentState.STOPPING, AgentState.STOPPED):
            return

        self.state = AgentState.STOPPING
        try:
            await self._shutdown()
        finally:
            self.state = AgentState.STOPPED
            await self._publish_event("agent.stopped", {"agent": self.config.name})

    async def health_check(self) -> Dict[str, Any]:
        """Return standard health information."""
        return {
            "healthy": self.state in (AgentState.READY, AgentState.WORKING),
            "state": self.state.value,
            "agent": self.config.name,
            "agent_type": self.config.agent_type,
            "last_error": self.last_error,
            "uptime_seconds": self._uptime_seconds(),
        }

    def get_info(self) -> Dict[str, Any]:
        """Get serializable metadata for this agent."""
        return {
            "name": self.config.name,
            "type": self.config.agent_type,
            "description": self.config.description,
            "priority": self.config.priority.value,
            "timeout_seconds": self.config.timeout_seconds,
            "tags": self.config.tags,
            "state": self.state.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }

    async def run_method(self, method_name: str, **kwargs) -> TaskResult:
        """Invoke a named async method with timeout + lifecycle state handling."""
        target = getattr(self, method_name, None)
        if target is None or method_name.startswith("_"):
            return TaskResult(success=False, error=f"Unknown method: {method_name}")

        if not asyncio.iscoroutinefunction(target):
            return TaskResult(success=False, error=f"Method is not async: {method_name}")

        started = datetime.utcnow()
        previous_state = self.state
        self.state = AgentState.WORKING
        try:
            result = await asyncio.wait_for(target(**kwargs), timeout=self.config.timeout_seconds)
            elapsed_ms = int((datetime.utcnow() - started).total_seconds() * 1000)
            return TaskResult(success=True, data=result, duration_ms=elapsed_ms)
        except Exception as exc:
            self.last_error = str(exc)
            elapsed_ms = int((datetime.utcnow() - started).total_seconds() * 1000)
            logger.error(
                "Agent %s method %s failed: %s",
                self.config.name,
                method_name,
                exc,
                exc_info=True,
            )
            return TaskResult(success=False, error=str(exc), duration_ms=elapsed_ms)
        finally:
            if self.state != AgentState.STOPPED:
                self.state = previous_state if previous_state != AgentState.WORKING else AgentState.READY

    async def _publish_event(self, event_name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Publish events tagged with this agent as the source."""
        await self.event_bus.publish(
            event_name,
            data or {},
            source_agent_id=self.config.name,
        )

    def _uptime_seconds(self) -> Optional[float]:
        if not self.started_at:
            return None
        return round((datetime.utcnow() - self.started_at).total_seconds(), 3)

    async def _initialize(self) -> None:
        raise NotImplementedError

    async def _shutdown(self) -> None:
        raise NotImplementedError
