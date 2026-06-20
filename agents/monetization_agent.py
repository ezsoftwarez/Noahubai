"""
Monetization Agent - Plan awareness, upsell recommendations, license guidance.

Wraps the entitlement service and exposes monetization logic to the UI
and other agents without coupling them to license key parsing.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from core import BaseAgent, AgentConfig, AgentPriority
from backend.entitlements import (
    FEATURE_MATRIX,
    PlanTier,
    entitlement_service,
)

logger = logging.getLogger(__name__)

UPGRADE_HINTS: Dict[str, Dict[str, str]] = {
    "pro.advanced_memory_search": {
        "title": "Advanced memory search",
        "benefit": "Search patterns and session history across all projects.",
        "plan": "pro",
    },
    "pro.background_automation": {
        "title": "Background automation",
        "benefit": "Run recipes while you code — fixes and sync on autopilot.",
        "plan": "pro",
    },
    "pro.local_analytics": {
        "title": "Local analytics",
        "benefit": "See growth metrics, success rates, and agent performance.",
        "plan": "pro",
    },
    "pro.audit_trail": {
        "title": "Audit trail",
        "benefit": "Full action history for debugging and compliance.",
        "plan": "pro",
    },
    "team.shared_workspaces": {
        "title": "Shared workspaces",
        "benefit": "Collaborate with your studio on the same project brain.",
        "plan": "team",
    },
    "team.managed_sync": {
        "title": "Managed sync",
        "benefit": "Cloud relay so the team stays in sync without manual export.",
        "plan": "team",
    },
}

PLAN_SUMMARY: Dict[str, Dict[str, Any]] = {
    PlanTier.FREE.value: {
        "label": "Free",
        "tagline": "Local core + BYOK for single-user workflows",
        "price_hint": "$0",
    },
    PlanTier.PRO.value: {
        "label": "Pro",
        "tagline": "Advanced memory, automation, analytics, audit",
        "price_hint": "Workflow tier",
    },
    PlanTier.TEAM.value: {
        "label": "Team",
        "tagline": "Shared workspaces, team knowledge, managed sync",
        "price_hint": "Studio tier",
    },
}


class MonetizationAgent(BaseAgent):
    """Entitlements, upsell recommendations, and license activation guidance."""

    def __init__(self, state_manager, event_bus):
        config = AgentConfig(
            name="monetization_agent",
            agent_type="monetization",
            description="Manages plan tiers, license activation, and upgrade recommendations",
            priority=AgentPriority.NORMAL,
            timeout_seconds=15,
            tags=["billing", "entitlements", "upsell"],
        )
        super().__init__(config, event_bus, state_manager)

    async def _initialize(self) -> None:
        ctx = entitlement_service.resolve()
        await self.state_manager.set(
            "monetization:last_plan",
            ctx.plan.value,
        )
        logger.info("Monetization agent ready (plan=%s)", ctx.plan.value)

    async def _shutdown(self) -> None:
        logger.info("Monetization agent shutting down")

    async def get_status(self) -> Dict[str, Any]:
        """Current plan, features, and pricing summary."""
        ctx = entitlement_service.resolve()
        plan = ctx.plan.value
        return {
            "plan": plan,
            "plan_summary": PLAN_SUMMARY.get(plan, {}),
            "features": sorted(ctx.features),
            "feature_count": len(ctx.features),
            "license_id": ctx.license_id,
            "activated_at": ctx.activated_at,
            "strict_mode": ctx.strict_mode,
            "available_plans": [t.value for t in PlanTier],
        }

    async def get_recommendations(self) -> Dict[str, Any]:
        """Upsell suggestions for features not on the current plan."""
        ctx = entitlement_service.resolve()
        missing: List[Dict[str, str]] = []

        for feature_id, hint in UPGRADE_HINTS.items():
            if feature_id not in ctx.features:
                missing.append(
                    {
                        "feature_id": feature_id,
                        "title": hint["title"],
                        "benefit": hint["benefit"],
                        "required_plan": hint["plan"],
                    }
                )

        next_plan = None
        if ctx.plan == PlanTier.FREE:
            next_plan = PlanTier.PRO.value
        elif ctx.plan == PlanTier.PRO:
            next_plan = PlanTier.TEAM.value

        return {
            "current_plan": ctx.plan.value,
            "next_suggested_plan": next_plan,
            "recommendations": missing[:6],
            "total_locked_features": len(missing),
        }

    async def get_pricing(self) -> Dict[str, Any]:
        """Public pricing matrix for UI display."""
        return {
            "plans": {
                tier.value: {
                    **PLAN_SUMMARY[tier.value],
                    "feature_count": len(FEATURE_MATRIX[tier]),
                    "highlights": _plan_highlights(tier),
                }
                for tier in PlanTier
            },
            "model": "open_core_byok",
            "documentation": "docs/PRICING.md",
        }

    async def activate_license(self, license_key: str) -> Dict[str, Any]:
        """Activate Pro or Team license."""
        try:
            ctx = entitlement_service.activate_license(license_key)
        except ValueError as exc:
            return {"status": "error", "error": str(exc)}

        await self.state_manager.set("monetization:last_plan", ctx.plan.value)
        await self._publish_event(
            "monetization.license_activated",
            {"plan": ctx.plan.value, "license_id": ctx.license_id},
        )
        return {"status": "activated", "entitlements": ctx.to_dict()}


def _plan_highlights(tier: PlanTier) -> List[str]:
    if tier == PlanTier.FREE:
        return [
            "Cursor bridge + local chat",
            "BYOK providers",
            "Memory, issue, fix agents",
        ]
    if tier == PlanTier.PRO:
        return [
            "Advanced memory search",
            "Background automation",
            "Analytics + audit trail",
        ]
    return [
        "Shared workspaces",
        "Team knowledge base",
        "Managed sync / relay",
    ]
