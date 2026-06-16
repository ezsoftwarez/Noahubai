"""
State Manager - Centralized state management with isolation
"""
import logging
from typing import Any, Dict, Optional
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StateManager:
    """
    Centralized state management for the system.
    Maintains shared state while ensuring agent isolation.
    """
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = __import__('asyncio').Lock()
    
    # ==================== Basic State Operations ====================
    
    async def set(self, key: str, value: Any, ttl_seconds: int = None) -> None:
        """Set a state value"""
        async with self._lock:
            self._state[key] = value
            self._metadata[key] = {
                "updated_at": datetime.utcnow().isoformat(),
                "ttl_seconds": ttl_seconds,
                "created_at": self._metadata.get(key, {}).get("created_at", datetime.utcnow().isoformat())
            }
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get a state value"""
        async with self._lock:
            if key not in self._state:
                return default
            
            # Check TTL
            meta = self._metadata.get(key, {})
            if meta.get("ttl_seconds"):
                updated = datetime.fromisoformat(meta["updated_at"])
                if datetime.utcnow() - updated > timedelta(seconds=meta["ttl_seconds"]):
                    del self._state[key]
                    del self._metadata[key]
                    return default
            
            return self._state.get(key, default)
    
    async def delete(self, key: str) -> bool:
        """Delete a state value"""
        async with self._lock:
            if key in self._state:
                del self._state[key]
                del self._metadata[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if state key exists"""
        return await self.get(key) is not None
    
    # ==================== Collection Operations ====================
    
    async def append_to_list(self, key: str, value: Any) -> None:
        """Append to a list in state"""
        async with self._lock:
            if key not in self._state:
                self._state[key] = []
            
            if not isinstance(self._state[key], list):
                raise ValueError(f"State '{key}' is not a list")
            
            self._state[key].append(value)
            self._metadata[key] = {
                "updated_at": datetime.utcnow().isoformat(),
                "type": "list"
            }
    
    async def get_list(self, key: str) -> list:
        """Get list from state"""
        value = await self.get(key)
        return value if isinstance(value, list) else []
    
    async def merge_dict(self, key: str, data: Dict) -> None:
        """Merge dict into state"""
        async with self._lock:
            if key not in self._state:
                self._state[key] = {}
            
            if not isinstance(self._state[key], dict):
                raise ValueError(f"State '{key}' is not a dict")
            
            self._state[key].update(data)
            self._metadata[key] = {
                "updated_at": datetime.utcnow().isoformat(),
                "type": "dict"
            }
    
    async def get_dict(self, key: str) -> dict:
        """Get dict from state"""
        value = await self.get(key)
        return value if isinstance(value, dict) else {}
    
    # ==================== Batch Operations ====================
    
    async def get_all(self) -> Dict[str, Any]:
        """Get all state"""
        async with self._lock:
            return dict(self._state)
    
    async def clear(self) -> None:
        """Clear all state"""
        async with self._lock:
            self._state.clear()
            self._metadata.clear()
    
    async def get_keys(self, prefix: str = None) -> list:
        """Get all state keys, optionally filtered by prefix"""
        async with self._lock:
            keys = list(self._state.keys())
            if prefix:
                keys = [k for k in keys if k.startswith(prefix)]
            return keys
    
    # ==================== Memory-Based Issue Tracking ====================
    
    async def log_issue(self, issue: Dict) -> str:
        """
        Log an issue to be remembered and tracked
        
        Args:
            issue: Issue dict with 'type', 'message', 'context', 'severity'
            
        Returns:
            Issue ID
        """
        import uuid
        issue_id = str(uuid.uuid4())
        
        issue_record = {
            "id": issue_id,
            "type": issue.get("type", "unknown"),
            "message": issue.get("message", ""),
            "context": issue.get("context", {}),
            "severity": issue.get("severity", "info"),  # info, warning, error, critical
            "timestamp": datetime.utcnow().isoformat(),
            "status": "open",  # open, investigating, resolved
            "attempts": [],
            "related_issues": [],
        }
        
        await self.append_to_list("system:issues", issue_record)
        logger.info(f"Logged issue {issue_id}: {issue.get('message')}")
        
        return issue_id
    
    async def get_issues(self, status: str = None, severity: str = None) -> list:
        """
        Retrieve remembered issues
        
        Args:
            status: Filter by status (open, investigating, resolved)
            severity: Filter by severity level
            
        Returns:
            List of issues
        """
        issues = await self.get_list("system:issues")
        
        if status:
            issues = [i for i in issues if i.get("status") == status]
        if severity:
            issues = [i for i in issues if i.get("severity") == severity]
        
        return issues
    
    async def update_issue(self, issue_id: str, update_data: Dict) -> bool:
        """Update an issue"""
        issues = await self.get_list("system:issues")
        
        for issue in issues:
            if issue["id"] == issue_id:
                issue.update(update_data)
                await self.set("system:issues", issues)
                return True
        
        return False
    
    async def record_fix_attempt(self, issue_id: str, attempt: Dict) -> bool:
        """Record a fix attempt for an issue"""
        issues = await self.get_list("system:issues")
        
        for issue in issues:
            if issue["id"] == issue_id:
                attempt_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "strategy": attempt.get("strategy", ""),
                    "result": attempt.get("result", ""),
                    "success": attempt.get("success", False),
                    "details": attempt.get("details", {}),
                }
                issue["attempts"].append(attempt_record)
                
                if attempt.get("success"):
                    issue["status"] = "resolved"
                
                await self.set("system:issues", issues)
                return True
        
        return False
    
    # ==================== Memory-Based Learning ====================
    
    async def remember(self, category: str, key: str, value: Any) -> None:
        """
        Store a memory/fact for future reference
        
        Args:
            category: Memory category (e.g., 'patterns', 'solutions', 'errors')
            key: Memory key
            value: Memory content
        """
        memory_key = f"memory:{category}"
        memory = await self.get_dict(memory_key)
        
        memory[key] = {
            "content": value,
            "learned_at": datetime.utcnow().isoformat(),
            "access_count": memory.get(key, {}).get("access_count", 0) + 1
        }
        
        await self.merge_dict(memory_key, memory)
        logger.debug(f"Remembered {category}:{key}")
    
    async def recall(self, category: str, key: str = None) -> Dict:
        """
        Recall learned memories
        
        Args:
            category: Memory category
            key: Optional specific key, otherwise return all
            
        Returns:
            Memory or memories
        """
        memory_key = f"memory:{category}"
        memory = await self.get_dict(memory_key)
        
        if key:
            if key in memory:
                # Increment access count while returning plain content to callers.
                memory[key]["access_count"] = memory[key].get("access_count", 0) + 1
                await self.merge_dict(memory_key, memory)
                record = memory[key]
                return record.get("content", record)
            return None

        # Return plain content values so agent logic can consume memories directly.
        return {
            item_key: item_value.get("content", item_value)
            for item_key, item_value in memory.items()
        }
    
    async def forget(self, category: str, key: str) -> bool:
        """Remove a memory"""
        memory_key = f"memory:{category}"
        memory = await self.get_dict(memory_key)
        
        if key in memory:
            del memory[key]
            await self.merge_dict(memory_key, memory)
            return True
        
        return False
    
    # ==================== Growth & Learning ====================
    
    async def record_action(self, action: Dict) -> None:
        """
        Record an action for learning and optimization
        
        Args:
            action: Action dict with 'type', 'agent', 'params', 'result'
        """
        action_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": action.get("type", ""),
            "agent": action.get("agent", ""),
            "params": action.get("params", {}),
            "result": action.get("result", ""),
            "success": action.get("success", False),
            "duration_ms": action.get("duration_ms", 0),
        }
        
        await self.append_to_list("system:action_history", action_record)
    
    async def get_action_history(self, agent: str = None, limit: int = 100) -> list:
        """Get action history for learning"""
        history = await self.get_list("system:action_history")
        
        if agent:
            history = [a for a in history if a.get("agent") == agent]
        
        return history[-limit:]
    
    async def get_statistics(self) -> Dict:
        """Get system statistics for growth"""
        issues = await self.get_list("system:issues")
        actions = await self.get_list("system:action_history")
        
        resolved_issues = [i for i in issues if i.get("status") == "resolved"]
        successful_actions = [a for a in actions if a.get("success")]
        
        return {
            "total_issues_logged": len(issues),
            "issues_resolved": len(resolved_issues),
            "issues_open": len([i for i in issues if i.get("status") == "open"]),
            "total_actions": len(actions),
            "successful_actions": len(successful_actions),
            "success_rate": len(successful_actions) / len(actions) if actions else 0,
            "avg_resolution_time": self._calc_avg_resolution_time(resolved_issues),
        }
    
    @staticmethod
    def _calc_avg_resolution_time(issues: list) -> float:
        """Calculate average time to resolve issues"""
        if not issues:
            return 0
        
        times = []
        for issue in issues:
            if issue.get("attempts"):
                first_attempt = issue["attempts"][0].get("timestamp")
                last_attempt = issue["attempts"][-1].get("timestamp")
                
                if first_attempt and last_attempt:
                    start = datetime.fromisoformat(first_attempt)
                    end = datetime.fromisoformat(last_attempt)
                    times.append((end - start).total_seconds())
        
        return sum(times) / len(times) if times else 0
