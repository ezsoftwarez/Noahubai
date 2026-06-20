"""Tests for entitlement and license logic."""
import os

import pytest

from backend.entitlements import (
    EntitlementService,
    PlanTier,
    FEATURE_MATRIX,
    generate_license_key,
    parse_license_key,
    entitlement_service,
)


def test_free_tier_default(monkeypatch):
    monkeypatch.delenv("NOAHUBAI_LICENSE_KEY", raising=False)
    monkeypatch.delenv("NOAHUBAI_PLAN", raising=False)
    svc = EntitlementService()
    svc._cached = None
    ctx = svc.resolve(force_refresh=True)
    assert ctx.plan == PlanTier.FREE
    assert "core.cursor_bridge" in ctx.features


def test_plan_override(monkeypatch):
    monkeypatch.setenv("NOAHUBAI_PLAN", "pro")
    monkeypatch.delenv("NOAHUBAI_LICENSE_KEY", raising=False)
    svc = EntitlementService()
    svc._cached = None
    ctx = svc.resolve(force_refresh=True)
    assert ctx.plan == PlanTier.PRO
    assert "pro.advanced_memory_search" in ctx.features


def test_license_key_roundtrip():
    key = generate_license_key(PlanTier.PRO, "test-user")
    parsed = parse_license_key(key)
    assert parsed is not None
    tier, license_id, _ = parsed
    assert tier == PlanTier.PRO
    assert license_id == "test-user"


def test_invalid_license_key():
    assert parse_license_key("invalid-key") is None
    assert parse_license_key("NHUB-pro-fake-tampered") is None


def test_feature_matrix_includes_core_for_all_tiers():
    core = FEATURE_MATRIX[PlanTier.FREE]
    for tier in (PlanTier.PRO, PlanTier.TEAM):
        assert core.issubset(FEATURE_MATRIX[tier])


def test_strict_mode_blocks_premium(monkeypatch):
    monkeypatch.setenv("NOAHUBAI_PLAN", "free")
    monkeypatch.setenv("NOAHUBAI_ENTITLEMENTS_STRICT", "true")
    monkeypatch.delenv("NOAHUBAI_LICENSE_KEY", raising=False)
    svc = EntitlementService()
    svc._cached = None
    allowed, missing = svc.check_path("/api/memory/search")
    assert not allowed
    assert missing == "pro.advanced_memory_search"


def test_pro_allows_premium_route(monkeypatch):
    monkeypatch.setenv("NOAHUBAI_PLAN", "pro")
    monkeypatch.delenv("NOAHUBAI_LICENSE_KEY", raising=False)
    svc = EntitlementService()
    svc._cached = None
    allowed, missing = svc.check_path("/api/memory/search")
    assert allowed
    assert missing is None
