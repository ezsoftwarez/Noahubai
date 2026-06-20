"""Tests for monetization agent."""
import pytest

from agents.monetization_agent import MonetizationAgent, PLAN_SUMMARY
from backend.entitlements import PlanTier, generate_license_key
from core import EventBus, StateManager


@pytest.fixture
def monetization_agent():
    bus = EventBus()
    state = StateManager()
    agent = MonetizationAgent(state, bus)
    return agent, state, bus


@pytest.mark.asyncio
async def test_get_status_default(monetization_agent):
    agent, _, _ = monetization_agent
    await agent.initialize()
    status = await agent.get_status()
    assert status["plan"] == PlanTier.FREE.value
    assert "features" in status
    assert status["plan_summary"]["label"] == "Free"


@pytest.mark.asyncio
async def test_get_recommendations_suggests_upgrades(monetization_agent):
    agent, _, _ = monetization_agent
    await agent.initialize()
    recs = await agent.get_recommendations()
    assert recs["current_plan"] == "free"
    assert recs["next_suggested_plan"] == "pro"
    assert len(recs["recommendations"]) > 0


@pytest.mark.asyncio
async def test_get_pricing_includes_all_plans(monetization_agent):
    agent, _, _ = monetization_agent
    await agent.initialize()
    pricing = await agent.get_pricing()
    assert set(pricing["plans"].keys()) == {"free", "pro", "team"}
    for tier in PlanTier:
        assert tier.value in PLAN_SUMMARY


@pytest.mark.asyncio
async def test_activate_license(monetization_agent, monkeypatch):
    agent, _, _ = monetization_agent
    await agent.initialize()
    key = generate_license_key(PlanTier.PRO, "test-ui")
    result = await agent.activate_license(key)
    assert result["status"] == "activated"
    assert result["entitlements"]["plan"] == "pro"
