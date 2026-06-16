"""
Agent registry and runtime orchestration helpers.
"""
from __future__ import annotations

import inspect
import logging
import time
from datetime import datetime
from typing import Any

from .agent_framework import AgentState, BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Track, initialize, and invoke Noahubai agents."""

    def __init__(self, event_bus: Any, state_manager: Any):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.agents: dict[str, BaseAgent] = {}
        self._metrics: dict[str, dict[str, Any]] = {}

    async def register(self, agent: BaseAgent) -> None:
        """Register an agent instance with the runtime."""
        name = agent.config.name
        if name in self.agents:
            raise ValueError(f"Agent already registered: {name}")

        self.agents[name] = agent
        self._metrics[name] = {
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "last_called_at": None,
            "last_duration_ms": 0,
            "average_duration_ms": 0.0,
        }
        logger.info("Registered agent %s", name)

    async def initialize_all(self) -> bool:
        """Initialize every registered agent."""
        if not self.agents:
            return True

        results = []
        for agent in self.agents.values():
            results.append(await agent.initialize())
        return all(results)

    async def shutdown_all(self) -> None:
        """Shutdown all agents in reverse registration order."""
        for agent in reversed(list(self.agents.values())):
            await agent.shutdown()

    def get_agent(self, name: str) -> BaseAgent | None:
        """Retrieve a registered agent by name."""
        return self.agents.get(name)

    def list_agents(self) -> list[dict[str, Any]]:
        """Return public summaries for all registered agents."""
        return [self.agents[name].get_info() for name in sorted(self.agents)]

    async def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Collect health reports for every agent."""
        return {name: await agent.health_check() for name, agent in self.agents.items()}

    async def get_agent_metrics(self, name: str) -> dict[str, Any]:
        """Return runtime metrics for one agent."""
        metrics = self._metrics.get(name)
        if metrics is None:
            raise LookupError(f"Agent not found: {name}")
        return dict(metrics)

    async def restart_agent(self, name: str) -> bool:
        """Restart an agent by name."""
        agent = self.get_agent(name)
        if not agent:
            return False

        stopped = await agent.shutdown()
        started = await agent.initialize()
        return stopped and started

    async def call_agent(self, name: str, method_name: str, **kwargs: Any) -> Any:
        """Invoke an agent method and record runtime metrics."""
        agent = self.get_agent(name)
        if agent is None:
            raise LookupError(f"Agent not found: {name}")

        method = getattr(agent, method_name, None)
        if not callable(method):
            raise AttributeError(f"Agent '{name}' has no callable '{method_name}'")

        started_at = time.perf_counter()
        agent.last_task_started_at = time.time()
        previous_state = agent.state
        agent.state = AgentState.WORKING
        success = False
        result: Any = None
        error_text: str | None = None

        try:
            maybe_result = method(**kwargs)
            result = await maybe_result if inspect.isawaitable(maybe_result) else maybe_result
            success = True
            return result
        except Exception as exc:
            error_text = str(exc)
            agent.last_error = error_text
            agent.state = AgentState.ERROR
            logger.exception("Agent call failed: %s.%s", name, method_name)
            raise
        finally:
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            if success:
                agent.last_error = None
                agent.state = AgentState.READY if agent.initialized else previous_state

            self._update_metrics(name, duration_ms, success)
            await self.state_manager.record_action(
                {
                    "type": method_name,
                    "agent": name,
                    "params": kwargs,
                    "result": result if success else error_text,
                    "success": success,
                    "duration_ms": duration_ms,
                    "recorded_at": datetime.utcnow().isoformat(),
                }
            )

    def _update_metrics(self, name: str, duration_ms: int, success: bool) -> None:
        """Update rolling metrics for an agent call."""
        metrics = self._metrics[name]
        metrics["calls"] += 1
        if success:
            metrics["successes"] += 1
        else:
            metrics["failures"] += 1
        metrics["last_called_at"] = datetime.utcnow().isoformat()
        metrics["last_duration_ms"] = duration_ms

        calls = metrics["calls"]
        prev_avg = metrics["average_duration_ms"]
        metrics["average_duration_ms"] = ((prev_avg * (calls - 1)) + duration_ms) / calls
