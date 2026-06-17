"""
Agent Framework - Base class and lifecycle for detached agents
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent lifecycle states"""
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentPriority(int, Enum):
    """Agent priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str
    agent_type: str
    description: str = ""
    priority: AgentPriority = AgentPriority.NORMAL
    timeout_seconds: int = 30
    tags: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of an agent task execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0


class BaseAgent:
  """
  Base class for all Noahubai agents.
  Subclasses implement _initialize() and _shutdown().
  """

  def __init__(self, config: AgentConfig, event_bus, state_manager):
    self.config = config
    self.event_bus = event_bus
    self.state_manager = state_manager
    self.state = AgentState.CREATED
    self._initialized = False
    self._metrics = {
      "tasks_completed": 0,
      "tasks_failed": 0,
      "last_activity": None,
      "uptime_start": None,
    }

  @property
  def name(self) -> str:
    return self.config.name

  async def initialize(self) -> bool:
    """Initialize the agent"""
    try:
      self.state = AgentState.INITIALIZING
      await self._initialize()
      self._initialized = True
      self.state = AgentState.READY
      self._metrics["uptime_start"] = datetime.utcnow().isoformat()
      await self._publish_event("agent.initialized", {"agent": self.name})
      logger.info(f"Agent {self.name} initialized")
      return True
    except Exception as e:
      self.state = AgentState.ERROR
      logger.error(f"Failed to initialize agent {self.name}: {e}", exc_info=True)
      return False

  async def shutdown(self) -> None:
    """Gracefully shut down the agent"""
    try:
      await self._shutdown()
      self.state = AgentState.SHUTDOWN
      await self._publish_event("agent.shutdown", {"agent": self.name})
      logger.info(f"Agent {self.name} shut down")
    except Exception as e:
      logger.error(f"Error shutting down agent {self.name}: {e}", exc_info=True)

  async def _initialize(self) -> None:
    """Override in subclasses for initialization logic"""
    raise NotImplementedError

  async def _shutdown(self) -> None:
    """Override in subclasses for shutdown logic"""
    raise NotImplementedError

  async def _publish_event(self, event_name: str, data: Dict = None) -> None:
    """Publish an event to the event bus"""
    if self.event_bus:
      await self.event_bus.publish(
        event_name,
        data or {},
        source_agent_id=self.name,
      )

  async def health_check(self) -> Dict[str, Any]:
    """Return agent health status"""
    return {
      "healthy": self.state == AgentState.READY,
      "state": self.state.value,
      "initialized": self._initialized,
      "name": self.name,
      "type": self.config.agent_type,
    }

  def get_info(self) -> Dict[str, Any]:
    """Return agent metadata"""
    return {
      "name": self.config.name,
      "type": self.config.agent_type,
      "description": self.config.description,
      "priority": self.config.priority.name,
      "state": self.state.value,
      "tags": self.config.tags,
      "timeout_seconds": self.config.timeout_seconds,
    }

  def get_metrics(self) -> Dict[str, Any]:
    """Return agent performance metrics"""
    return dict(self._metrics)

  async def call_method(self, method_name: str, **kwargs) -> Any:
    """Invoke a public method on this agent with timeout"""
    if not self._initialized:
      raise RuntimeError(f"Agent {self.name} is not initialized")

    method = getattr(self, method_name, None)
    if method is None or method_name.startswith("_"):
      raise AttributeError(f"Method '{method_name}' not found on agent {self.name}")

    self.state = AgentState.BUSY

    try:
      if asyncio.iscoroutinefunction(method):
        result = await asyncio.wait_for(
          method(**kwargs),
          timeout=self.config.timeout_seconds,
        )
      else:
        result = method(**kwargs)

      self._metrics["tasks_completed"] += 1
      self._metrics["last_activity"] = datetime.utcnow().isoformat()
      return result
    except asyncio.TimeoutError:
      self._metrics["tasks_failed"] += 1
      raise TimeoutError(
        f"Method '{method_name}' on agent {self.name} timed out "
        f"after {self.config.timeout_seconds}s"
      )
    except Exception:
      self._metrics["tasks_failed"] += 1
      raise
    finally:
      if self.state == AgentState.BUSY:
        self.state = AgentState.READY
