"""
Entitlements and license management for Noahubai.

Open-core model: free tier is default; Pro/Team unlock workflow features
via license key or environment override. No Stripe dependency in core.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, FrozenSet, Optional, Set

logger = logging.getLogger(__name__)

LICENSE_FILE = Path(__file__).resolve().parent.parent / "config" / "license.json"
LICENSE_PREFIX = "NHUB"


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


# Features gated by plan (workflow value, not token usage)
FEATURE_MATRIX: Dict[PlanTier, FrozenSet[str]] = {
    PlanTier.FREE: frozenset(
        {
            "core.local_chat",
            "core.cursor_bridge",
            "core.byok_providers",
            "core.transcript_import",
            "core.basic_projects",
            "core.single_machine_agents",
            "core.memory_learn",
            "core.issue_detect",
            "core.auto_fix_basic",
        }
    ),
    PlanTier.PRO: frozenset(
        {
            "core.local_chat",
            "core.cursor_bridge",
            "core.byok_providers",
            "core.transcript_import",
            "core.basic_projects",
            "core.single_machine_agents",
            "core.memory_learn",
            "core.issue_detect",
            "core.auto_fix_basic",
            "pro.advanced_memory_search",
            "pro.multi_project_orchestration",
            "pro.background_automation",
            "pro.premium_import_export",
            "pro.local_analytics",
            "pro.audit_trail",
            "pro.installer_channel",
        }
    ),
    PlanTier.TEAM: frozenset(
        {
            "core.local_chat",
            "core.cursor_bridge",
            "core.byok_providers",
            "core.transcript_import",
            "core.basic_projects",
            "core.single_machine_agents",
            "core.memory_learn",
            "core.issue_detect",
            "core.auto_fix_basic",
            "pro.advanced_memory_search",
            "pro.multi_project_orchestration",
            "pro.background_automation",
            "pro.premium_import_export",
            "pro.local_analytics",
            "pro.audit_trail",
            "pro.installer_channel",
            "team.shared_workspaces",
            "team.knowledge_base",
            "team.permissioned_agents",
            "team.activity_audit",
            "team.managed_sync",
        }
    ),
}

# API route -> required feature (premium endpoints)
ROUTE_FEATURES: Dict[str, str] = {
    "/api/memory/search": "pro.advanced_memory_search",
    "/api/memory/export": "pro.premium_import_export",
    "/api/automation/recipes": "pro.background_automation",
    "/api/analytics/summary": "pro.local_analytics",
    "/api/audit/events": "pro.audit_trail",
    "/api/team/workspaces": "team.shared_workspaces",
    "/api/team/knowledge": "team.knowledge_base",
    "/api/team/sync": "team.managed_sync",
}


@dataclass
class EntitlementContext:
    """Resolved entitlements for the current request."""

    plan: PlanTier
    features: Set[str] = field(default_factory=set)
    license_id: Optional[str] = None
    activated_at: Optional[str] = None
    strict_mode: bool = False

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan": self.plan.value,
            "features": sorted(self.features),
            "license_id": self.license_id,
            "activated_at": self.activated_at,
            "strict_mode": self.strict_mode,
        }


def _secret() -> bytes:
    """Local signing secret; override in production via env."""
    return os.getenv("NOAHUBAI_LICENSE_SECRET", "noahubai-dev-secret-change-me").encode()


def _normalize_tier(raw: str) -> PlanTier:
    try:
        return PlanTier(raw.lower().strip())
    except ValueError:
        return PlanTier.FREE


def generate_license_key(tier: PlanTier, license_id: str = "local-dev") -> str:
    """
    Generate a signed license key for testing or manual issuance.

    Format: NHUB-{tier}-{license_id}-{signature}
    """
    payload = f"{tier.value}:{license_id}"
    sig = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "-", license_id)[:32]
    return f"{LICENSE_PREFIX}-{tier.value}-{safe_id}-{sig}"


def parse_license_key(key: str) -> Optional[tuple[PlanTier, str, str]]:
    """Parse and verify a license key. Returns (tier, license_id, signature) or None."""
    if not key or not key.startswith(f"{LICENSE_PREFIX}-"):
        return None

    parts = key.split("-")
    if len(parts) < 4:
        return None

    tier_raw = parts[1]
    sig = parts[-1]
    license_id = "-".join(parts[2:-1])

    try:
        tier = PlanTier(tier_raw)
    except ValueError:
        return None

    payload = f"{tier.value}:{license_id}"
    expected = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(expected, sig):
        return None

    return tier, license_id, sig


def _load_persisted_license() -> Optional[Dict[str, Any]]:
    if not LICENSE_FILE.exists():
        return None
    try:
        return json.loads(LICENSE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read license file: %s", exc)
        return None


def _save_persisted_license(data: Dict[str, Any]) -> None:
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LICENSE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


class EntitlementService:
    """Resolve plan tier and features from env, file, or activated license."""

    def __init__(self) -> None:
        self._cached: Optional[EntitlementContext] = None

    def strict_mode(self) -> bool:
        return os.getenv("NOAHUBAI_ENTITLEMENTS_STRICT", "false").lower() in (
            "1",
            "true",
            "yes",
        )

    def resolve(self, force_refresh: bool = False) -> EntitlementContext:
        if self._cached is not None and not force_refresh:
            return self._cached

        plan = PlanTier.FREE
        license_id: Optional[str] = None
        activated_at: Optional[str] = None

        # 1) Explicit plan override (dev / enterprise deploy)
        env_plan = os.getenv("NOAHUBAI_PLAN")
        if env_plan:
            plan = _normalize_tier(env_plan)

        # 2) License key from env
        env_key = os.getenv("NOAHUBAI_LICENSE_KEY")
        if env_key:
            parsed = parse_license_key(env_key.strip())
            if parsed:
                plan, license_id, _ = parsed
                activated_at = datetime.now(timezone.utc).isoformat()

        # 3) Persisted license file (unless env key wins)
        if not env_key:
            persisted = _load_persisted_license()
            if persisted and persisted.get("license_key"):
                parsed = parse_license_key(persisted["license_key"])
                if parsed:
                    plan, license_id, _ = parsed
                    activated_at = persisted.get("activated_at")

        ctx = EntitlementContext(
            plan=plan,
            features=set(FEATURE_MATRIX[plan]),
            license_id=license_id,
            activated_at=activated_at,
            strict_mode=self.strict_mode(),
        )
        self._cached = ctx
        return ctx

    def activate_license(self, license_key: str) -> EntitlementContext:
        parsed = parse_license_key(license_key.strip())
        if not parsed:
            raise ValueError("Invalid or tampered license key")

        tier, license_id, _ = parsed
        activated_at = datetime.now(timezone.utc).isoformat()
        _save_persisted_license(
            {
                "license_key": license_key.strip(),
                "plan": tier.value,
                "license_id": license_id,
                "activated_at": activated_at,
            }
        )
        self._cached = None
        logger.info("Activated license: plan=%s id=%s", tier.value, license_id)
        return self.resolve(force_refresh=True)

    def required_feature_for_path(self, path: str) -> Optional[str]:
        # Exact match first, then prefix for nested routes
        if path in ROUTE_FEATURES:
            return ROUTE_FEATURES[path]
        for route_prefix, feature in ROUTE_FEATURES.items():
            if path.startswith(route_prefix.rstrip("/") + "/"):
                return feature
        return None

    def check_path(self, path: str) -> tuple[bool, Optional[str]]:
        """Return (allowed, missing_feature)."""
        feature = self.required_feature_for_path(path)
        if feature is None:
            return True, None
        ctx = self.resolve()
        if ctx.has_feature(feature):
            return True, None
        if ctx.strict_mode:
            return False, feature
        # Non-strict: allow but log (dev-friendly)
        logger.debug("Premium route %s would require %s (non-strict)", path, feature)
        return True, feature


# Singleton for app lifetime
entitlement_service = EntitlementService()
