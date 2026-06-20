"""Tests for monetization agent."""
import pytest

from agents.monetization_agent import MonetizationAgent, PLAN_SUMMARY
from backend.entitlements import PlanTier, generate_license_key, entitlement_service
from core import EventBus, StateManager


@pytest.fixture
def monetization_agent():
    bus = EventBus()
    state = StateManager()
    agent = MonetizationAgent(state, bus)
    return agent, state, bus


@pytest.mark.asyncio
async def test_get_status_default(monetization_agent, monkeypatch):
    monkeypatch.setattr(
        "backend.entitlements._load_persisted_license",
        lambda: None,
    )
    monkeypatch.delenv("NOAHUBAI_LICENSE_KEY", raising=False)
    monkeypatch.delenv("NOAHUBAI_PLAN", raising=False)
    entitlement_service._cached = None
    agent, _, _ = monetization_agent
    await agent.initialize()
    status = await agent.get_status()
    assert status["plan"] == PlanTier.FREE.value
    assert "features" in status
    assert status["plan_summary"]["label"] == "Free"


@pytest.mark.asyncio
async def test_get_recommendations_suggests_upgrades(monetization_agent, monkeypatch):
    monkeypatch.setattr(
        "backend.entitlements._load_persisted_license",
        lambda: None,
    )
    monkeypatch.delenv("NOAHUBAI_LICENSE_KEY", raising=False)
    monkeypatch.delenv("NOAHUBAI_PLAN", raising=False)
    entitlement_service._cached = None
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
async def test_get_summary_single_resolve(monetization_agent, monkeypatch):
    agent, _, _ = monetization_agent
    await agent.initialize()
    calls = {"n": 0}
    original = __import__("backend.entitlements", fromlist=["entitlement_service"]).entitlement_service.resolve

    def counting_resolve(force_refresh=False):
        calls["n"] += 1
        return original(force_refresh=force_refresh)

    monkeypatch.setattr(
        "backend.entitlements.entitlement_service.resolve",
        counting_resolve,
    )
    summary = await agent.get_summary()
    assert "status" in summary and "recommendations" in summary and "pricing" in summary
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_activate_license(monetization_agent, monkeypatch):
    agent, _, _ = monetization_agent
    await agent.initialize()
    key = generate_license_key(PlanTier.PRO, "test-ui")
    result = await agent.activate_license(key)
    assert result["status"] == "activated"
    assert result["entitlements"]["plan"] == "pro"

