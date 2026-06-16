"""
Agent registry and lifecycle orchestration.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .agent_framework import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Tracks registered agents and provides call/restart orchestration."""

    def __init__(self, event_bus, state_manager):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.agents: Dict[str, BaseAgent] = {}
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def register(self, agent: BaseAgent) -> None:
        """Register an agent instance."""
        async with self._lock:
            if agent.config.name in self.agents:
                raise ValueError(f"Agent already registered: {agent.config.name}")

            self.agents[agent.config.name] = agent
            self._metrics[agent.config.name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "avg_duration_ms": 0.0,
                "last_called_at": None,
                "last_error": None,
            }

    async def initialize_all(self) -> bool:
        """Initialize all agents concurrently."""
        tasks = [agent.initialize() for agent in self.agents.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return all(result is True for result in results)

    async def shutdown_all(self) -> None:
        """Shutdown all agents concurrently."""
        if not self.agents:
            return
        await asyncio.gather(*(agent.shutdown() for agent in self.agents.values()), return_exceptions=True)

    def list_agents(self) -> list[Dict[str, Any]]:
        """List metadata for all registered agents."""
        return [agent.get_info() for agent in self.agents.values()]

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name."""
        return self.agents.get(agent_name)

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks for all agents."""
        checks = await asyncio.gather(
            *(agent.health_check() for agent in self.agents.values()),
            return_exceptions=True,
        )
        result: Dict[str, Dict[str, Any]] = {}
        for agent, check in zip(self.agents.values(), checks):
            if isinstance(check, Exception):
                result[agent.config.name] = {
                    "healthy": False,
                    "state": "error",
                    "error": str(check),
                }
            else:
                result[agent.config.name] = check
        return result

    async def get_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Get invocation metrics for a specific agent."""
        metrics = self._metrics.get(agent_name)
        if metrics is None:
            raise ValueError(f"Agent not found: {agent_name}")
        return dict(metrics)

    async def restart_agent(self, agent_name: str) -> bool:
        """Restart one registered agent."""
        agent = self.get_agent(agent_name)
        if not agent:
            return False

        await agent.shutdown()
        return await agent.initialize()

    async def call_agent(self, agent_name: str, method_name: str, **kwargs) -> Any:
        """Invoke an agent method and track call metrics."""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent not found: {agent_name}")

        result = await agent.run_method(method_name, **kwargs)
        self._record_metrics(agent_name, result.duration_ms, result.success, result.error)

        await self.state_manager.record_action(
            {
                "type": method_name,
                "agent": agent_name,
                "params": kwargs,
                "success": result.success,
                "result": "ok" if result.success else "error",
                "duration_ms": result.duration_ms,
            }
        )

        if not result.success:
            raise RuntimeError(result.error or f"{agent_name}.{method_name} failed")

        return result.data

    def _record_metrics(
        self,
        agent_name: str,
        duration_ms: int,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        metrics = self._metrics[agent_name]
        metrics["total_calls"] += 1
        metrics["last_called_at"] = datetime.utcnow().isoformat()

        if success:
            metrics["successful_calls"] += 1
            metrics["last_error"] = None
        else:
            metrics["failed_calls"] += 1
            metrics["last_error"] = error

        calls = metrics["total_calls"]
        previous_avg = metrics["avg_duration_ms"]
        metrics["avg_duration_ms"] = ((previous_avg * (calls - 1)) + duration_ms) / calls
