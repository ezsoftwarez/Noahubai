"""
Issue Agent - Detects, tracks, and categorizes issues
PURPOSE: Remember issues and track them for resolution
"""
from core import BaseAgent, AgentConfig, AgentPriority
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class IssueAgent(BaseAgent):
    """Intelligent issue detection and tracking agent"""
    
    def __init__(self, state_manager, event_bus):
        config = AgentConfig(
            name="issue_agent",
            agent_type="issue",
            description="Detects, remembers, and tracks system issues",
            priority=AgentPriority.CRITICAL,
            timeout_seconds=30,
            tags=["issues", "monitoring", "tracking"]
        )
        super().__init__(config, event_bus, state_manager)
    
    async def _initialize(self) -> None:
        """Initialize issue tracking"""
        # Initialize issue database
        issues = await self.state_manager.get_list("system:issues")
        logger.info(f"Issue agent initialized with {len(issues)} existing issues")
    
    async def _shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Issue agent shutting down")
    
    # ==================== Issue Detection ====================
    
    async def detect_issue(self, issue: Dict) -> str:
        """
        Detect and log a new issue
        
        Args:
            issue: Issue details (type, message, severity, context)
            
        Returns:
            Issue ID
        """
        issue_id = await self.state_manager.log_issue(issue)
        
        severity = issue.get("severity", "info")
        await self._publish_event(f"issue.detected.{severity}", {
            "issue_id": issue_id,
            "issue_type": issue.get("type"),
            "message": issue.get("message"),
        })
        
        logger.info(f"Issue detected: {issue_id} ({issue.get('type')})")
        return issue_id
    
    async def get_issue(self, issue_id: str) -> Dict:
        """Retrieve a specific issue"""
        issues = await self.state_manager.get_list("system:issues")
        
        for issue in issues:
            if issue["id"] == issue_id:
                return issue
        
        return {"error": "Issue not found"}
    
    async def list_issues(self, status: str = None, severity: str = None) -> Dict:
        """
        List issues with optional filtering
        
        Args:
            status: Filter by status (open, investigating, resolved)
            severity: Filter by severity (info, warning, error, critical)
            
        Returns:
            List of issues
        """
        issues = await self.state_manager.get_issues(status=status, severity=severity)
        
        return {
            "status": "retrieved",
            "total": len(issues),
            "filters": {"status": status, "severity": severity},
            "issues": issues
        }
    
    # ==================== Issue Analysis ====================
    
    async def analyze_issues(self) -> Dict:
        """
        Analyze all issues and generate insights
        
        Returns:
            Analysis with patterns and recommendations
        """
        issues = await self.state_manager.get_list("system:issues")
        
        analysis = {
            "total_issues": len(issues),
            "by_status": self._count_by_field(issues, "status"),
            "by_severity": self._count_by_field(issues, "severity"),
            "by_type": self._count_by_field(issues, "type"),
            "oldest_issue": self._get_oldest_issue(issues),
            "most_common_type": self._get_most_common_type(issues),
            "patterns": await self._identify_patterns(issues),
        }
        
        await self._publish_event("issue.analyzed", analysis)
        
        return analysis
    
    @staticmethod
    def _count_by_field(issues: List, field: str) -> Dict[str, int]:
        """Count issues by a specific field"""
        counts = {}
        for issue in issues:
            value = issue.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    @staticmethod
    def _get_oldest_issue(issues: List) -> Dict:
        """Get the oldest unresolved issue"""
        unresolved = [i for i in issues if i.get("status") != "resolved"]
        if unresolved:
            return min(unresolved, key=lambda x: x.get("timestamp", ""))
        return {}
    
    @staticmethod
    def _get_most_common_type(issues: List) -> str:
        """Get the most frequently occurring issue type"""
        types = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            types[issue_type] = types.get(issue_type, 0) + 1
        return max(types, key=types.get) if types else "unknown"
    
    async def _identify_patterns(self, issues: List) -> Dict:
        """Identify patterns across issues"""
        patterns = {}
        
        # Time-based patterns
        patterns["clustering"] = self._detect_time_clustering(issues)
        
        # Relationship patterns
        patterns["related_issues"] = self._find_related_issues(issues)
        
        return patterns
    
    @staticmethod
    def _detect_time_clustering(issues: List) -> str:
        """Detect if issues cluster at specific times"""
        if len(issues) < 3:
            return "insufficient_data"
        
        # Simple clustering detection
        timestamps = [i.get("timestamp", "") for i in issues if i.get("timestamp")]
        if not timestamps:
            return "no_time_data"
        
        # In production, use proper time clustering algorithms
        return "distributed"  # Placeholder
    
    @staticmethod
    def _find_related_issues(issues: List) -> List:
        """Find related issues based on type/context"""
        related = []
        
        # Group by type
        by_type = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue["id"])
        
        # Find groups with multiple issues
        for issue_type, issue_ids in by_type.items():
            if len(issue_ids) > 1:
                related.append({"type": issue_type, "count": len(issue_ids), "ids": issue_ids})
        
        return related
    
    # ==================== Issue Status Management ====================
    
    async def update_status(self, issue_id: str, status: str) -> Dict:
        """
        Update issue status
        
        Args:
            issue_id: ID of issue to update
            status: New status (open, investigating, resolved)
            
        Returns:
            Updated issue
        """
        success = await self.state_manager.update_issue(issue_id, {
            "status": status,
            "status_updated_at": datetime.utcnow().isoformat()
        })
        
        if success:
            await self._publish_event(f"issue.status_changed.{status}", {
                "issue_id": issue_id
            })
            logger.info(f"Issue {issue_id} status updated to {status}")
            return {"status": "updated", "issue_id": issue_id}
        
        return {"error": "Issue not found"}
    
    async def mark_investigating(self, issue_id: str, details: Dict = None) -> Dict:
        """Mark issue as under investigation"""
        return await self.update_status(issue_id, "investigating")
    
    async def mark_resolved(self, issue_id: str, resolution: str = "") -> Dict:
        """Mark issue as resolved"""
        success = await self.state_manager.update_issue(issue_id, {
            "status": "resolved",
            "resolution": resolution,
            "resolved_at": datetime.utcnow().isoformat()
        })
        
        if success:
            await self._publish_event("issue.resolved", {
                "issue_id": issue_id,
                "resolution": resolution
            })
            return {"status": "resolved", "issue_id": issue_id}
        
        return {"error": "Issue not found"}
