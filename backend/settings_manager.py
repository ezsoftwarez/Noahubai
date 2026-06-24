"""
Settings Management - Advanced configuration system for Noahubai
Handles agent settings, system configuration, and advanced customization
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SettingsManager:
    """Advanced settings management for all agents and system"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    # ==================== Agent Settings ====================
    
    async def get_agent_settings(self, agent_name: str) -> Dict[str, Any]:
        """
        Get all settings for an agent
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Agent settings
        """
        settings_key = f"settings:agents:{agent_name}"
        settings = await self.state_manager.get_dict(settings_key)
        return settings if settings else {}
    
    async def update_agent_setting(self, agent_name: str, key: str, value: Any) -> bool:
        """
        Update a single agent setting
        
        Args:
            agent_name: Name of agent
            key: Setting key
            value: New value
            
        Returns:
            True if successful
        """
        settings = await self.get_agent_settings(agent_name)
        settings[key] = value
        
        settings_key = f"settings:agents:{agent_name}"
        await self.state_manager.merge_dict(settings_key, {key: value})
        
        await self.state_manager.record_action({
            "type": "setting_change",
            "agent": agent_name,
            "setting": key,
            "value": value,
            "success": True
        })
        
        logger.info(f"Updated {agent_name} setting: {key} = {value}")
        return True
    
    async def update_agent_settings(self, agent_name: str, updates: Dict[str, Any]) -> Dict[str, bool]:
        """
        Update multiple agent settings
        
        Args:
            agent_name: Name of agent
            updates: Dict of settings to update
            
        Returns:
            Dict mapping setting keys to success status
        """
        results = {}
        
        for key, value in updates.items():
            try:
                success = await self.update_agent_setting(agent_name, key, value)
                results[key] = success
            except Exception as e:
                logger.error(f"Failed to update {agent_name}.{key}: {e}")
                results[key] = False
        
        return results
    
    async def reset_agent_settings(self, agent_name: str, to_defaults: Dict[str, Any]) -> bool:
        """
        Reset agent settings to defaults
        
        Args:
            agent_name: Name of agent
            to_defaults: Default settings
            
        Returns:
            True if successful
        """
        settings_key = f"settings:agents:{agent_name}"
        await self.state_manager.set(settings_key, to_defaults)
        
        logger.info(f"Reset {agent_name} settings to defaults")
        return True
    
    # ==================== System Settings ====================
    
    async def get_system_settings(self) -> Dict[str, Any]:
        """Get all system settings"""
        return await self.state_manager.get_dict("settings:system")
    
    async def update_system_setting(self, key: str, value: Any) -> bool:
        """Update a system setting"""
        await self.state_manager.merge_dict("settings:system", {key: value})
        logger.info(f"Updated system setting: {key} = {value}")
        return True
    
    # ==================== Performance Tuning ====================
    
    async def get_performance_config(self) -> Dict[str, Any]:
        """Get performance tuning configuration"""
        return {
            "memory_agent": {
                "pattern_cache_size": await self._get_setting("memory_agent", "pattern_cache_size", 500),
                "solution_cache_ttl": await self._get_setting("memory_agent", "solution_cache_ttl", 3600),
                "learning_batch_size": await self._get_setting("memory_agent", "learning_batch_size", 10),
            },
            "issue_agent": {
                "detection_batch_interval": await self._get_setting("issue_agent", "detection_batch_interval", 5),
                "pattern_analysis_threshold": await self._get_setting("issue_agent", "pattern_analysis_threshold", 3),
                "cleanup_interval_hours": await self._get_setting("issue_agent", "cleanup_interval_hours", 24),
            },
            "fixer_agent": {
                "fix_strategy_timeout": await self._get_setting("fixer_agent", "fix_strategy_timeout", 120),
                "parallel_fixes": await self._get_setting("fixer_agent", "parallel_fixes", 3),
                "rollback_enabled": await self._get_setting("fixer_agent", "rollback_enabled", True),
            },
            "system": {
                "event_bus_max_history": await self._get_setting("system", "event_bus_max_history", 10000),
                "state_backup_interval": await self._get_setting("system", "state_backup_interval", 3600),
                "garbage_collection_interval": await self._get_setting("system", "garbage_collection_interval", 1800),
            }
        }
    
    async def update_performance_config(self, config: Dict[str, Any]) -> Dict[str, bool]:
        """Update performance configuration"""
        results = {}
        
        for agent, settings in config.items():
            for key, value in settings.items():
                setting_key = f"performance:{agent}:{key}"
                try:
                    await self.state_manager.set(setting_key, value)
                    results[f"{agent}:{key}"] = True
                except Exception as e:
                    logger.error(f"Failed to update performance setting: {e}")
                    results[f"{agent}:{key}"] = False
        
        return results
    
    # ==================== Logging & Debug ====================
    
    async def set_log_level(self, level: str, agent_name: str = None) -> bool:
        """
        Set logging level
        
        Args:
            level: DEBUG, INFO, WARNING, ERROR, CRITICAL
            agent_name: Optional specific agent
        """
        log_key = f"logging:{agent_name or 'system'}:level"
        await self.state_manager.set(log_key, level)
        logger.info(f"Set log level to {level}")
        return True
    
    async def enable_debug_mode(self, agent_name: str = None) -> bool:
        """Enable debug mode"""
        return await self.set_log_level("DEBUG", agent_name)
    
    async def get_debug_config(self) -> Dict[str, Any]:
        """Get debug configuration"""
        return {
            "debug_enabled": await self.state_manager.get("debug:enabled", False),
            "log_events": await self.state_manager.get("debug:log_events", False),
            "trace_calls": await self.state_manager.get("debug:trace_calls", False),
            "detailed_errors": await self.state_manager.get("debug:detailed_errors", False),
        }
    
    # ==================== Persistence & Backup ====================
    
    async def create_settings_backup(self) -> Dict[str, Any]:
        """Create backup of all settings"""
        backup = {
            "timestamp": datetime.utcnow().isoformat(),
            "agents": {},
            "system": await self.get_system_settings(),
        }
        
        for agent in ["memory_agent", "issue_agent", "fixer_agent"]:
            backup["agents"][agent] = await self.get_agent_settings(agent)
        
        backup_key = f"backups:settings:{backup['timestamp']}"
        await self.state_manager.set(backup_key, backup)
        
        logger.info(f"Created settings backup: {backup_key}")
        return backup
    
    async def restore_settings_backup(self, backup_timestamp: str) -> bool:
        """Restore settings from backup"""
        backup_key = f"backups:settings:{backup_timestamp}"
        backup = await self.state_manager.get(backup_key)
        
        if not backup:
            logger.error(f"Backup not found: {backup_key}")
            return False
        
        # Restore agent settings
        for agent, settings in backup.get("agents", {}).items():
            await self.reset_agent_settings(agent, settings)
        
        # Restore system settings
        await self.state_manager.set("settings:system", backup.get("system", {}))
        
        logger.info(f"Restored settings from backup: {backup_timestamp}")
        return True
    
    async def list_settings_backups(self) -> List[Dict[str, Any]]:
        """List available settings backups"""
        keys = await self.state_manager.get_keys("backups:settings:")
        backups = []
        
        for key in keys:
            backup = await self.state_manager.get(key)
            if backup:
                backups.append({
                    "timestamp": backup.get("timestamp"),
                    "key": key
                })
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    # ==================== Utility Methods ====================
    
    async def _get_setting(self, agent: str, key: str, default: Any) -> Any:
        """Internal helper to get a setting with default"""
        settings = await self.get_agent_settings(agent)
        return settings.get(key, default)
    
    async def validate_settings(self, agent_name: str, settings: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate settings before applying
        
        Returns:
            Dict of validation errors (empty if valid)
        """
        errors = {}
        
        # Example validation logic
        if "max_patterns" in settings:
            if not isinstance(settings["max_patterns"], int) or settings["max_patterns"] < 100:
                errors["max_patterns"] = "Must be integer >= 100"
        
        if "learning_rate" in settings:
            value = settings["learning_rate"]
            if not isinstance(value, (int, float)) or not (0.1 <= value <= 1.0):
                errors["learning_rate"] = "Must be number between 0.1 and 1.0"
        
        return errors
