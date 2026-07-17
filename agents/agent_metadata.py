"""
Agent Metadata and Configuration
Provides detailed information about all agents and their capabilities
"""
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProcessingCapability(Enum):
    """Data processing capabilities"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    ASYNC = "async"


@dataclass
class Skill:
    """Skill definition"""
    name: str
    level: SkillLevel
    description: str
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class SubAgent:
    """Sub-agent definition (micro-task handler)"""
    name: str
    role: str
    responsibility: str
    depends_on: List[str] = None
    provides: List[str] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.provides is None:
            self.provides = []


@dataclass
class API:
    """API endpoint definition"""
    method: str  # GET, POST, PUT, DELETE
    path: str
    description: str
    parameters: Dict[str, Any] = None
    response: str = ""
    requires_auth: bool = False

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class Hook:
    """Hook/Event definition"""
    event_name: str
    trigger: str
    payload: Dict[str, str]
    description: str


@dataclass
class MPCConfig:
    """Multi-Process Communication configuration"""
    enabled: bool = True
    protocol: str = "event_bus"  # event_bus, rpc, message_queue
    timeout_seconds: int = 30
    retry_attempts: int = 3
    parallel_workers: int = 4
    queue_size: int = 1000


@dataclass
class AgentMetadata:
    """Complete agent metadata"""
    name: str
    bio: str
    version: str
    author: str
    icon: str
    color: str
    priority: str
    status: str
    skills: List[Skill]
    sub_agents: List[SubAgent]
    apis: List[API]
    hooks: List[Hook]
    processing_capabilities: List[ProcessingCapability]
    mpc_config: MPCConfig
    settings: Dict[str, Any]


# ==================== Agent Definitions ====================

MEMORY_AGENT_METADATA = AgentMetadata(
    name="memory_agent",
    bio="🧠 Cognitive Memory System - Learns patterns, stores solutions, and enables continuous growth. Acts as the system's long-term memory, identifying recurring situations and building an intelligent knowledge base over time.",
    version="1.0.0",
    author="Noahubai Core",
    icon="🧠",
    color="#6366f1",
    priority="HIGH",
    status="active",
    skills=[
        Skill(
            name="Pattern Learning",
            level=SkillLevel.ADVANCED,
            description="Detect and memorize successful patterns",
            examples=["cache-on-load", "batch-processing", "rate-limiting"]
        ),
        Skill(
            name="Solution Storage",
            level=SkillLevel.EXPERT,
            description="Store and retrieve problem-solution mappings",
            examples=["timeout fixes", "memory optimization", "connection pooling"]
        ),
        Skill(
            name="Growth Analysis",
            level=SkillLevel.ADVANCED,
            description="Analyze and report system improvement metrics",
            examples=["success rates", "issue resolution times", "knowledge base growth"]
        ),
        Skill(
            name="Knowledge Recall",
            level=SkillLevel.EXPERT,
            description="Retrieve relevant knowledge for current situations",
            examples=["pattern matching", "solution recommendation", "context analysis"]
        )
    ],
    sub_agents=[
        SubAgent(
            name="pattern_detector",
            role="Pattern Recognition Engine",
            responsibility="Identifies recurring patterns in operations",
            provides=["detected_patterns", "pattern_metrics"]
        ),
        SubAgent(
            name="solution_keeper",
            role="Solution Database Manager",
            responsibility="Maintains and retrieves problem solutions",
            provides=["solutions", "effectiveness_scores"],
            depends_on=["pattern_detector"]
        ),
        SubAgent(
            name="growth_calculator",
            role="Metrics & Analytics Engine",
            responsibility="Computes growth and improvement metrics",
            provides=["growth_score", "recommendations", "statistics"],
            depends_on=["pattern_detector", "solution_keeper"]
        )
    ],
    apis=[
        API(method="POST", path="/memory/learn", description="Learn a new pattern"),
        API(method="GET", path="/memory/patterns", description="Retrieve learned patterns"),
        API(method="POST", path="/memory/solution", description="Store a solution"),
        API(method="GET", path="/memory/solution/{problem}", description="Get solution for problem"),
        API(method="GET", path="/memory/growth", description="Get growth metrics")
    ],
    hooks=[
        Hook("pattern.learned", "New pattern successfully stored", {"pattern_id": "string"}, "Triggered when system learns a pattern"),
        Hook("solution.stored", "Solution saved to knowledge base", {"problem": "string"}, "Triggered when solution is stored"),
        Hook("growth.updated", "Growth metrics recalculated", {"score": "number"}, "Triggered when growth improves")
    ],
    processing_capabilities=[ProcessingCapability.ASYNC, ProcessingCapability.BATCH],
    mpc_config=MPCConfig(
        enabled=True,
        protocol="event_bus",
        timeout_seconds=60,
        parallel_workers=2
    ),
    settings={
        "max_patterns": {"type": "integer", "default": 1000, "min": 100, "max": 10000, "description": "Maximum patterns to store"},
        "max_solutions": {"type": "integer", "default": 500, "min": 50, "max": 5000, "description": "Maximum solutions to remember"},
        "learning_rate": {"type": "float", "default": 0.8, "min": 0.1, "max": 1.0, "description": "Pattern learning confidence threshold"},
        "cleanup_threshold": {"type": "integer", "default": 7, "min": 1, "max": 30, "description": "Days before old patterns are archived"},
    }
)

ISSUE_AGENT_METADATA = AgentMetadata(
    name="issue_agent",
    bio="🔍 Issue Detection & Tracking System - Monitors, detects, and remembers all system issues. Acts as a vigilant observer that never forgets a problem, tracking issue lifecycle and identifying patterns across failures.",
    version="1.0.0",
    author="Noahubai Core",
    icon="🔍",
    color="#ec4899",
    priority="CRITICAL",
    status="active",
    skills=[
        Skill(
            name="Issue Detection",
            level=SkillLevel.EXPERT,
            description="Detect and categorize system issues",
            examples=["timeout errors", "memory leaks", "connection failures"]
        ),
        Skill(
            name="Pattern Analysis",
            level=SkillLevel.ADVANCED,
            description="Identify patterns across multiple issues",
            examples=["recurring failures", "time-based clusters", "related problems"]
        ),
        Skill(
            name="Issue Tracking",
            level=SkillLevel.EXPERT,
            description="Maintain complete issue lifecycle",
            examples=["status transitions", "resolution tracking", "history logging"]
        ),
        Skill(
            name="Severity Assessment",
            level=SkillLevel.ADVANCED,
            description="Evaluate issue impact and urgency",
            examples=["critical alert", "warning classification", "priority ranking"]
        )
    ],
    sub_agents=[
        SubAgent(
            name="issue_detector",
            role="Issue Recognition Engine",
            responsibility="Detects new issues in the system",
            provides=["detected_issues", "issue_metadata"]
        ),
        SubAgent(
            name="issue_categorizer",
            role="Classification & Tagging System",
            responsibility="Categorizes issues by type and severity",
            provides=["categorized_issues", "severity_ratings"],
            depends_on=["issue_detector"]
        ),
        SubAgent(
            name="pattern_analyzer",
            role="Pattern Recognition Engine",
            responsibility="Finds relationships between issues",
            provides=["related_issues", "pattern_insights"],
            depends_on=["issue_categorizer"]
        ),
        SubAgent(
            name="issue_lifecycle_manager",
            role="State Management System",
            responsibility="Manages issue status transitions",
            provides=["status_updates", "history_logs"],
            depends_on=["issue_categorizer"]
        )
    ],
    apis=[
        API(method="POST", path="/issues/detect", description="Detect new issue"),
        API(method="GET", path="/issues", description="List issues"),
        API(method="GET", path="/issues/{id}", description="Get issue details"),
        API(method="GET", path="/issues/analysis", description="Analyze all issues"),
        API(method="POST", path="/issues/{id}/status", description="Update issue status")
    ],
    hooks=[
        Hook("issue.detected", "New issue detected", {"issue_id": "string", "severity": "string"}, "When system detects an issue"),
        Hook("issue.status_changed", "Issue status updated", {"issue_id": "string", "new_status": "string"}, "When issue status transitions"),
        Hook("issue.pattern_found", "Pattern detected across issues", {"pattern_type": "string", "issue_count": "integer"}, "When related issues are found")
    ],
    processing_capabilities=[ProcessingCapability.REAL_TIME, ProcessingCapability.ASYNC],
    mpc_config=MPCConfig(
        enabled=True,
        protocol="event_bus",
        timeout_seconds=30,
        parallel_workers=4
    ),
    settings={
        "detection_sensitivity": {"type": "integer", "default": 3, "min": 1, "max": 5, "description": "How sensitive to issues (1=strict, 5=loose)"},
        "max_open_issues": {"type": "integer", "default": 500, "min": 50, "max": 5000, "description": "Maximum open issues to track"},
        "issue_retention_days": {"type": "integer", "default": 90, "min": 7, "max": 365, "description": "Days to keep resolved issues"},
        "pattern_threshold": {"type": "float", "default": 0.7, "min": 0.1, "max": 1.0, "description": "Confidence for pattern detection"}
    }
)

FIXER_AGENT_METADATA = AgentMetadata(
    name="fixer_agent",
    bio="🔧 Intelligent Problem Solver - Automatically fixes issues using learned solutions and smart strategies. Acts as the system's repair mechanism, learning from past fixes and improving resolution effectiveness.",
    version="1.0.0",
    author="Noahubai Core",
    icon="🔧",
    color="#10b981",
    priority="HIGH",
    status="active",
    skills=[
        Skill(
            name="Solution Application",
            level=SkillLevel.EXPERT,
            description="Apply known solutions to issues",
            examples=["execute fix steps", "verify resolution", "rollback on failure"]
        ),
        Skill(
            name="Strategy Generation",
            level=SkillLevel.ADVANCED,
            description="Create custom fix strategies for new issues",
            examples=["timeout handling", "resource optimization", "service restart"]
        ),
        Skill(
            name="Adaptive Fixing",
            level=SkillLevel.ADVANCED,
            description="Learn and adapt fixing strategies",
            examples=["adjust parameters", "try alternatives", "improve effectiveness"]
        ),
        Skill(
            name="Risk Management",
            level=SkillLevel.ADVANCED,
            description="Assess and manage fix risks",
            examples=["safe rollback", "validation checks", "impact analysis"]
        )
    ],
    sub_agents=[
        SubAgent(
            name="solution_applier",
            role="Known-Solution Executor",
            responsibility="Executes pre-established fixes",
            provides=["fix_results", "success_status"]
        ),
        SubAgent(
            name="strategy_engine",
            role="Fix Strategy Generator",
            responsibility="Creates strategies for unknown issues",
            provides=["fix_strategies", "step_sequences"],
            depends_on=["solution_applier"]
        ),
        SubAgent(
            name="safety_checker",
            role="Risk & Validation System",
            responsibility="Ensures fixes are safe and effective",
            provides=["safety_approval", "validation_results"],
            depends_on=["solution_applier", "strategy_engine"]
        ),
        SubAgent(
            name="learning_engine",
            role="Improvement & Optimization System",
            responsibility="Learns from fix successes and failures",
            provides=["effectiveness_metrics", "optimization_hints"],
            depends_on=["solution_applier", "safety_checker"]
        )
    ],
    apis=[
        API(method="POST", path="/fix/issue/{id}", description="Fix specific issue"),
        API(method="POST", path="/fix/all", description="Fix all open issues"),
        API(method="GET", path="/fix/history", description="Get fix history")
    ],
    hooks=[
        Hook("fix.started", "Fix operation started", {"issue_id": "string", "strategy": "string"}, "When fixing begins"),
        Hook("fix.completed", "Fix operation completed", {"issue_id": "string", "success": "boolean"}, "When fixing finishes"),
        Hook("fix.learned", "System learned from fix", {"solution_effectiveness": "number"}, "When fix improves future solutions")
    ],
    processing_capabilities=[ProcessingCapability.ASYNC, ProcessingCapability.BATCH],
    mpc_config=MPCConfig(
        enabled=True,
        protocol="event_bus",
        timeout_seconds=120,
        parallel_workers=3
    ),
    settings={
        "max_retry_attempts": {"type": "integer", "default": 3, "min": 1, "max": 10, "description": "Maximum fix attempts per issue"},
        "fix_timeout_seconds": {"type": "integer", "default": 120, "min": 10, "max": 600, "description": "Timeout for single fix operation"},
        "learning_mode": {"type": "string", "default": "adaptive", "enum": ["strict", "adaptive", "aggressive"], "description": "How aggressively to learn from fixes"},
        "parallel_fix_limit": {"type": "integer", "default": 3, "min": 1, "max": 10, "description": "Max issues to fix simultaneously"}
    }
)

# ==================== Agent Registry ====================

AGENT_METADATA = {
    "memory_agent": MEMORY_AGENT_METADATA,
    "issue_agent": ISSUE_AGENT_METADATA,
    "fixer_agent": FIXER_AGENT_METADATA,
}


def get_agent_metadata(agent_name: str) -> AgentMetadata:
    """Get metadata for a specific agent"""
    return AGENT_METADATA.get(agent_name)


def get_all_agents_metadata() -> Dict[str, AgentMetadata]:
    """Get metadata for all agents"""
    return AGENT_METADATA


def list_agent_names() -> List[str]:
    """List all agent names"""
    return list(AGENT_METADATA.keys())


def get_agent_skills(agent_name: str) -> List[Skill]:
    """Get skills for an agent"""
    metadata = get_agent_metadata(agent_name)
    return metadata.skills if metadata else []


def get_agent_sub_agents(agent_name: str) -> List[SubAgent]:
    """Get sub-agents for an agent"""
    metadata = get_agent_metadata(agent_name)
    return metadata.sub_agents if metadata else []


def get_agent_apis(agent_name: str) -> List[API]:
    """Get APIs for an agent"""
    metadata = get_agent_metadata(agent_name)
    return metadata.apis if metadata else []


def get_agent_hooks(agent_name: str) -> List[Hook]:
    """Get hooks for an agent"""
    metadata = get_agent_metadata(agent_name)
    return metadata.hooks if metadata else []
