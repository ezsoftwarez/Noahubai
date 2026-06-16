"""
Memory Agent - Handles system memory, learning, and knowledge retention
PURPOSE: Automatize growth through continuous memory and learning
"""
from core import BaseAgent, AgentConfig, AgentPriority
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryAgent(BaseAgent):
    """Intelligent memory and knowledge management agent"""
    
    def __init__(self, state_manager, event_bus):
        config = AgentConfig(
            name="memory_agent",
            agent_type="memory",
            description="Handles system memory, learning patterns, and knowledge retention",
            priority=AgentPriority.HIGH,
            timeout_seconds=60,
            tags=["learning", "memory", "growth"]
        )
        super().__init__(config, event_bus, state_manager)
    
    async def _initialize(self) -> None:
        """Initialize memory structures"""
        # Initialize memory categories
        categories = [
            "patterns",
            "solutions",
            "errors",
            "performance",
            "user_preferences",
            "agent_behaviors"
        ]
        
        for category in categories:
            existing = await self.state_manager.recall(category)
            if not existing:
                await self.state_manager.remember(category, "initialized", {
                    "created_at": datetime.utcnow().isoformat()
                })
        
        logger.info(f"Memory agent initialized with {len(categories)} categories")
    
    async def _shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Memory agent shutting down")
    
    # ==================== Memory Operations ====================
    
    async def learn_pattern(self, pattern_id: str, pattern_data: Dict) -> Dict:
        """
        Learn a new pattern for future automation
        
        Args:
            pattern_id: Unique pattern identifier
            pattern_data: Pattern details (conditions, actions, outcomes)
            
        Returns:
            Confirmation with pattern details
        """
        pattern_record = {
            "id": pattern_id,
            "data": pattern_data,
            "learned_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
            "success_rate": 0,
        }
        
        await self.state_manager.remember("patterns", pattern_id, pattern_record)
        await self._publish_event("memory.pattern_learned", {
            "pattern_id": pattern_id,
            "pattern_data": pattern_data
        })
        
        return {
            "status": "learned",
            "pattern_id": pattern_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def recall_pattern(self, pattern_id: str = None) -> Dict:
        """
        Retrieve learned patterns for automation
        
        Args:
            pattern_id: Optional specific pattern, otherwise return all
            
        Returns:
            Pattern or patterns
        """
        if pattern_id:
            pattern = await self.state_manager.recall("patterns", pattern_id)
            return pattern if pattern else {"error": "Pattern not found"}
        
        patterns = await self.state_manager.recall("patterns")
        return {"patterns": patterns, "total": len(patterns)}
    
    async def store_solution(self, problem: str, solution: Dict) -> Dict:
        """
        Store a solution for a problem (learning from fixes)
        
        Args:
            problem: Problem description/ID
            solution: Solution details (steps, code, configs)
            
        Returns:
            Confirmation
        """
        solution_record = {
            "problem": problem,
            "steps": solution.get("steps", []),
            "code": solution.get("code", ""),
            "configs": solution.get("configs", {}),
            "stored_at": datetime.utcnow().isoformat(),
            "effectiveness": solution.get("effectiveness", 0),
        }
        
        await self.state_manager.remember("solutions", problem, solution_record)
        await self._publish_event("memory.solution_stored", {"problem": problem})
        
        return {
            "status": "stored",
            "problem": problem,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_solution(self, problem: str) -> Dict:
        """Retrieve a known solution"""
        solution = await self.state_manager.recall("solutions", problem)
        if solution:
            await self._publish_event("memory.solution_retrieved", {"problem": problem})
            return solution
        return {"error": "No solution found for this problem"}
    
    async def log_error_pattern(self, error: Dict) -> Dict:
        """
        Learn from errors to prevent future occurrences
        
        Args:
            error: Error details (type, message, context, cause)
            
        Returns:
            Error ID and analysis
        """
        import uuid
        error_id = str(uuid.uuid4())
        
        error_record = {
            "id": error_id,
            "type": error.get("type", "unknown"),
            "message": error.get("message", ""),
            "context": error.get("context", {}),
            "cause": error.get("cause", ""),
            "frequency": 1,
            "logged_at": datetime.utcnow().isoformat(),
        }
        
        await self.state_manager.remember("errors", error_id, error_record)
        
        # Check if similar error exists
        similar = await self._find_similar_errors(error.get("type"), error.get("message"))
        
        await self._publish_event("memory.error_logged", {
            "error_id": error_id,
            "error_type": error.get("type"),
            "similar_errors": len(similar)
        })
        
        return {
            "status": "logged",
            "error_id": error_id,
            "similar_errors": len(similar),
            "recommendation": await self._get_error_recommendation(error)
        }
    
    async def _find_similar_errors(self, error_type: str, message: str) -> List:
        """Find similar errors in memory"""
        errors = await self.state_manager.recall("errors")
        similar = []
        
        for error_id, error_data in errors.items():
            if error_data.get("type") == error_type:
                # Simple similarity check
                if error_type in message or message in error_data.get("message", ""):
                    similar.append(error_id)
        
        return similar
    
    async def _get_error_recommendation(self, error: Dict) -> str:
        """Get recommendation based on error analysis"""
        error_type = error.get("type", "")
        
        if "timeout" in error_type.lower():
            return "Increase timeout, optimize queries, or use caching"
        elif "memory" in error_type.lower():
            return "Review memory usage, clear unused state, implement garbage collection"
        elif "connection" in error_type.lower():
            return "Check network connectivity, retry with backoff, use connection pooling"
        else:
            return "Review logs, check dependencies, run diagnostics"
    
    async def get_growth_metrics(self) -> Dict:
        """
        Get system growth metrics based on learning
        
        Returns:
            Growth statistics and recommendations
        """
        stats = await self.state_manager.get_statistics()
        
        patterns = await self.state_manager.recall("patterns")
        solutions = await self.state_manager.recall("solutions")
        errors = await self.state_manager.recall("errors")
        
        growth_score = self._calculate_growth_score(stats, patterns, solutions)
        
        return {
            "status": "analyzed",
            "growth_score": growth_score,
            "metrics": stats,
            "knowledge_base": {
                "patterns": len(patterns),
                "solutions": len(solutions),
                "known_errors": len(errors),
            },
            "recommendations": await self._generate_recommendations(stats, growth_score)
        }
    
    @staticmethod
    def _calculate_growth_score(stats: Dict, patterns: Dict, solutions: Dict) -> float:
        """Calculate overall system growth score (0-100)"""
        score = 0
        
        # Success rate (40%)
        score += stats.get("success_rate", 0) * 40
        
        # Issue resolution (30%)
        total_issues = stats.get("total_issues_logged", 1)
        resolved = stats.get("issues_resolved", 0)
        score += (resolved / total_issues * 30) if total_issues > 0 else 0
        
        # Knowledge base (30%)
        knowledge = len(patterns) + len(solutions)
        score += min(knowledge / 10 * 30, 30)  # Cap at 30
        
        return min(score, 100)
    
    async def _generate_recommendations(self, stats: Dict, growth_score: float) -> List[str]:
        """Generate recommendations for system improvement"""
        recommendations = []
        
        if growth_score < 50:
            recommendations.append("System is still learning. Continue gathering data and patterns.")
        
        if stats.get("issues_open", 0) > 5:
            recommendations.append(f"High number of open issues ({stats['issues_open']}). Prioritize resolution.")
        
        if stats.get("success_rate", 0) < 0.8:
            recommendations.append("Success rate below 80%. Review failed actions and adjust strategies.")
        
        if growth_score >= 80:
            recommendations.append("System is mature. Consider deploying automation strategies.")
        
        return recommendations if recommendations else ["System is performing well. Maintain current patterns."]
