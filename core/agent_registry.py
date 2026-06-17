"""
Agent Registry - Discovery, lifecycle, and method dispatch for agents
"""
import logging
from typing import Any, Dict, List, Optional

from .agent_framework import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
  """Manages registration, initialization, and communication with agents"""

  def __init__(self, event_bus, state_manager):
    self.event_bus = event_bus
    self.state_manager = state_manager
    self.agents: Dict[str, BaseAgent] = {}

  async def register(self, agent: BaseAgent) -> None:
    """Register an agent"""
    self.agents[agent.name] = agent
    logger.info(f"Registered agent: {agent.name}")

  async def initialize_all(self) -> bool:
    """Initialize all registered agents"""
    results = []
    for name, agent in self.agents.items():
      success = await agent.initialize()
      results.append(success)
      if not success:
        logger.error(f"Failed to initialize agent: {name}")

    return all(results)

  async def shutdown_all(self) -> None:
    """Shut down all registered agents"""
    for agent in self.agents.values():
      await agent.shutdown()

  async def health_check_all(self) -> Dict[str, Dict]:
    """Run health checks on all agents"""
    health = {}
    for name, agent in self.agents.items():
      health[name] = await agent.health_check()
    return health

  def list_agents(self) -> List[Dict]:
    """List info for all registered agents"""
    return [agent.get_info() for agent in self.agents.values()]

  def get_agent(self, name: str) -> Optional[BaseAgent]:
    """Get an agent by name"""
    return self.agents.get(name)

  async def get_agent_metrics(self, name: str) -> Dict:
    """Get metrics for a specific agent"""
    agent = self.get_agent(name)
    if not agent:
      return {}
    return agent.get_metrics()

  async def restart_agent(self, name: str) -> bool:
    """Restart a specific agent"""
    agent = self.get_agent(name)
    if not agent:
      return False

    await agent.shutdown()
    return await agent.initialize()

  async def call_agent(self, agent_name: str, method_name: str, **kwargs) -> Any:
    """Call a method on a registered agent"""
    agent = self.get_agent(agent_name)
    if not agent:
      raise ValueError(f"Agent '{agent_name}' not found")

    return await agent.call_method(method_name, **kwargs)
