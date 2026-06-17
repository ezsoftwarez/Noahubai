import pytest

from agents.agent_metadata import FIXER_AGENT_METADATA
from agents.fixer_agent import FixerAgent
from backend.settings_manager import SettingsManager
from core import EventBus, StateManager


def test_fixer_metadata_does_not_advertise_removed_flags():
    settings = FIXER_AGENT_METADATA.settings

    assert "auto_fix_enabled" not in settings
    assert "safety_checks_enabled" not in settings
    assert "max_retry_attempts" in settings
    assert "fix_timeout_seconds" in settings


@pytest.mark.asyncio
async def test_settings_backup_omits_removed_feature_toggle_store():
    settings_manager = SettingsManager(StateManager())

    backup = await settings_manager.create_settings_backup()

    assert "features" not in backup
    assert set(backup["agents"]) == {"memory_agent", "issue_agent", "fixer_agent"}
    assert not hasattr(settings_manager, "enable_feature")
    assert not hasattr(settings_manager, "disable_feature")


@pytest.mark.asyncio
async def test_fixer_active_path_still_resolves_open_issue():
    state_manager = StateManager()
    event_bus = EventBus()
    fixer = FixerAgent(state_manager, event_bus)
    await fixer.initialize()

    issue_id = await state_manager.log_issue({
        "type": "timeout",
        "message": "Request exceeded expected duration",
        "severity": "warning",
    })

    result = await fixer.fix_issue(issue_id)

    assert result["status"] == "fixed"
    assert result["issue_id"] == issue_id

    issues = await state_manager.get_issues(status="resolved")
    assert len(issues) == 1
    assert issues[0]["id"] == issue_id

    events = await event_bus.get_history("issue.fixed")
    assert len(events) == 1
    assert events[0].data == {"issue_id": issue_id, "method": "auto_analysis"}
