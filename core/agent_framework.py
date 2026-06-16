"""
Core agent framework primitives used by the Noahubai runtime.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any

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


class AgentPriority(IntEnum):
    """Relative scheduling priority for agents."""

    LOW = 10
    MEDIUM = 20
    HIGH = 30
    CRITICAL = 40


@dataclass(slots=True)
class AgentConfig:
    """Static configuration for an agent instance."""

    name: str
    agent_type: str
    description: str
    priority: AgentPriority = AgentPriority.MEDIUM
    timeout_seconds: int = 30
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TaskResult:
    """Standard shape for agent task execution results."""

    success: bool
    data: Any = None
    error: str | None = None
    duration_ms: int = 0


class BaseAgent:
    """Base class for all Noahubai agents."""

    def __init__(self, config: AgentConfig, event_bus: Any, state_manager: Any):
        self.config = config
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.state = AgentState.IDLE
        self.initialized = False
        self.last_error: str | None = None
        self.started_at: float | None = None
        self.last_task_started_at: float | None = None

    async def initialize(self) -> bool:
        """Initialize the agent and publish lifecycle events."""
        if self.initialized:
            return True

        self.state = AgentState.STARTING
        self.last_error = None
        self.started_at = time.time()
        try:
            await self._initialize()
            self.initialized = True
            self.state = AgentState.READY
            await self._publish_event(
                "agent.initialized",
                {
                    "agent": self.config.name,
                    "type": self.config.agent_type,
                    "priority": int(self.config.priority),
                },
            )
            return True
        except Exception as exc:  # pragma: no cover - defensive logging path
            self.last_error = str(exc)
            self.state = AgentState.ERROR
            logger.exception("Agent %s failed to initialize", self.config.name)
            await self._publish_event(
                "agent.initialization_failed",
                {"agent": self.config.name, "error": self.last_error},
            )
            return False

    async def shutdown(self) -> bool:
        """Gracefully stop the agent."""
        if not self.initialized and self.state == AgentState.STOPPED:
            return True

        self.state = AgentState.STOPPING
        try:
            await self._shutdown()
            self.initialized = False
            self.state = AgentState.STOPPED
            await self._publish_event(
                "agent.stopped",
                {"agent": self.config.name, "type": self.config.agent_type},
            )
            return True
        except Exception as exc:  # pragma: no cover - defensive logging path
            self.last_error = str(exc)
            self.state = AgentState.ERROR
            logger.exception("Agent %s failed to shut down cleanly", self.config.name)
            return False

    async def health_check(self) -> dict[str, Any]:
        """Return a lightweight health snapshot for dashboards and API calls."""
        uptime_seconds = 0.0
        if self.started_at is not None:
            uptime_seconds = max(0.0, time.time() - self.started_at)

        return {
            "healthy": self.state not in {AgentState.ERROR, AgentState.STOPPED},
            "state": self.state.value,
            "initialized": self.initialized,
            "uptime_seconds": round(uptime_seconds, 3),
            "last_error": self.last_error,
            "timeout_seconds": self.config.timeout_seconds,
            "tags": list(self.config.tags),
        }

    def get_info(self) -> dict[str, Any]:
        """Return public-facing static information about this agent."""
        return {
            "name": self.config.name,
            "type": self.config.agent_type,
            "description": self.config.description,
            "priority": self.config.priority.name,
            "timeout_seconds": self.config.timeout_seconds,
            "tags": list(self.config.tags),
            "state": self.state.value,
        }

    async def _publish_event(self, event_name: str, data: dict[str, Any] | None = None) -> None:
        """Publish an event attributed to this agent."""
        await self.event_bus.publish(
            event_name,
            data or {},
            source_agent_id=self.config.name,
        )

    async def _initialize(self) -> None:
        """Hook for agent-specific startup work."""

    async def _shutdown(self) -> None:
        """Hook for agent-specific shutdown work."""
