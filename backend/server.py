"""
Core API Server - FastAPI backend for Noahubai
Handles all agent communication and provides REST/WebSocket interface
"""
import asyncio
import logging
from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from datetime import datetime
import json

from core import (
    BaseAgent, AgentRegistry, EventBus, StateManager,
    AgentConfig, AgentPriority
)
from agents.memory_agent import MemoryAgent
from agents.issue_agent import IssueAgent
from agents.fixer_agent import FixerAgent
from backend.entitlements import entitlement_service, PlanTier, generate_license_key
from backend.middleware import EntitlementMiddleware

logger = logging.getLogger(__name__)
FRONTEND_FILE = Path(__file__).resolve().parent.parent / "frontend" / "windows7_shell.html"

# Global instances
event_bus: EventBus = None
state_manager: StateManager = None
agent_registry: AgentRegistry = None
ws_connections: List[WebSocket] = []


# ==================== Startup/Shutdown ====================

async def startup_event():
    """Initialize system on startup"""
    global event_bus, state_manager, agent_registry
    
    logger.info("🚀 Starting Noahubai System...")
    
    # Initialize core components
    event_bus = EventBus()
    state_manager = StateManager()
    agent_registry = AgentRegistry(event_bus, state_manager)
    
    # Create and register agents
    agents = [
        MemoryAgent(state_manager, event_bus),
        IssueAgent(state_manager, event_bus),
        FixerAgent(state_manager, event_bus),
    ]
    
    for agent in agents:
        await agent_registry.register(agent)
    
    # Initialize all agents
    success = await agent_registry.initialize_all()
    
    if success:
        logger.info("✅ All agents initialized successfully")
        await event_bus.publish("system.startup_complete", {
            "agents": len(agents),
            "timestamp": datetime.utcnow().isoformat()
        })
    else:
        logger.error("❌ Failed to initialize some agents")
    
    # Subscribe to system events for WebSocket broadcasting
    await event_bus.subscribe("*", broadcast_event)


async def shutdown_event():
    """Graceful shutdown"""
    logger.info("🛑 Shutting down Noahubai System...")
    
    # Close WebSocket connections
    for ws in ws_connections:
        await ws.close()
    
    # Shutdown all agents
    if agent_registry:
        await agent_registry.shutdown_all()
    
    logger.info("✅ System shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    await startup_event()
    yield
    await shutdown_event()


# ==================== FastAPI Setup ====================

app = FastAPI(
    title="Noahubai API",
    description=(
        "Local AI engine for AI Hub — Memory, Issue Tracking, and Auto-Fixing. "
        "Open-core with Free/Pro/Team entitlements."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Entitlement enforcement (strict mode via NOAHUBAI_ENTITLEMENTS_STRICT)
app.add_middleware(EntitlementMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Event Broadcasting ====================

async def broadcast_event(event):
    """Broadcast events to all connected WebSocket clients"""
    if not ws_connections:
        return
    
    message = {
        "type": "event",
        "event_name": event.name,
        "data": event.data,
        "timestamp": event.timestamp.isoformat(),
    }
    
    # Remove dead connections
    dead_connections = []
    
    for ws in ws_connections:
        try:
            await ws.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send to WebSocket: {e}")
            dead_connections.append(ws)
    
    # Clean up dead connections
    for ws in dead_connections:
        ws_connections.remove(ws)


# ==================== Entitlements ====================

@app.get("/api/entitlements")
async def get_entitlements():
    """Current plan, enabled features, and license status."""
    from backend.entitlements import FEATURE_MATRIX

    ctx = entitlement_service.resolve()
    return {
        "entitlements": ctx.to_dict(),
        "available_plans": [t.value for t in PlanTier],
        "feature_matrix_summary": {
            tier.value: len(FEATURE_MATRIX[tier]) for tier in PlanTier
        },
        "documentation": {
            "product": "docs/PRODUCT.md",
            "pricing": "docs/PRICING.md",
        },
    }


@app.post("/api/entitlements/activate")
async def activate_entitlements(request: Dict[str, Any]):
    """Activate a Pro or Team license key."""
    license_key = request.get("license_key", "").strip()
    if not license_key:
        raise HTTPException(status_code=400, detail="license_key is required")
    try:
        ctx = entitlement_service.activate_license(license_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "activated", "entitlements": ctx.to_dict()}


@app.get("/api/entitlements/dev-key")
async def dev_license_key(tier: str = "pro"):
    """
    Generate a dev license key (non-production only).
    Disabled when NOAHUBAI_DISABLE_DEV_KEYS=true.
    """
    import os

    if os.getenv("NOAHUBAI_DISABLE_DEV_KEYS", "false").lower() in ("1", "true", "yes"):
        raise HTTPException(status_code=404, detail="Not found")
    try:
        plan = PlanTier(tier.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="tier must be free, pro, or team")
    if plan == PlanTier.FREE:
        raise HTTPException(status_code=400, detail="free tier does not need a key")
    key = generate_license_key(plan, license_id="dev")
    return {"license_key": key, "tier": plan.value}


# ==================== Premium (Pro/Team) API stubs ====================

@app.get("/api/memory/search")
async def search_memory(q: str = ""):
    """Pro: searchable session / pattern history."""
    patterns = await agent_registry.call_agent("memory_agent", "recall_pattern")
    query = q.lower()
    if query and isinstance(patterns, dict):
        filtered = {
            k: v
            for k, v in patterns.items()
            if query in k.lower() or query in str(v).lower()
        }
        return {"query": q, "results": filtered, "tier": "pro.advanced_memory_search"}
    return {"query": q, "results": patterns, "tier": "pro.advanced_memory_search"}


@app.get("/api/memory/export")
async def export_memory(format: str = "json"):
    """Pro: export memory patterns and solutions."""
    patterns = await agent_registry.call_agent("memory_agent", "recall_pattern")
    return {"format": format, "data": patterns, "tier": "pro.premium_import_export"}


@app.get("/api/automation/recipes")
async def list_automation_recipes():
    """Pro: background automation recipe catalog."""
    return {
        "recipes": [],
        "message": "Connect AI Hub automation packs or add recipes locally.",
        "tier": "pro.background_automation",
    }


@app.get("/api/analytics/summary")
async def analytics_summary():
    """Pro: local-first usage and growth analytics."""
    stats = await state_manager.get_statistics()
    growth = await agent_registry.call_agent("memory_agent", "get_growth_metrics")
    return {"statistics": stats, "growth": growth, "tier": "pro.local_analytics"}


@app.get("/api/audit/events")
async def audit_events(limit: int = 50):
    """Pro: audit trail of agent actions."""
    actions = await state_manager.get_action_history(limit=limit)
    return {"events": actions, "tier": "pro.audit_trail"}


@app.get("/api/team/workspaces")
async def team_workspaces():
    """Team: shared workspace list (managed sync required for production)."""
    return {
        "workspaces": [],
        "tier": "team.shared_workspaces",
        "message": "Enable Team plan and managed sync for shared workspaces.",
    }


@app.get("/api/team/knowledge")
async def team_knowledge():
    """Team: shared knowledge base index."""
    return {"documents": [], "tier": "team.knowledge_base"}


@app.get("/api/team/sync")
async def team_sync_status():
    """Team: managed relay / sync status."""
    return {"sync_enabled": False, "tier": "team.managed_sync"}


# ==================== Health & Status ====================

@app.get("/api/health")
async def health_check():
    """System health check"""
    agent_health = await agent_registry.health_check_all()
    
    all_healthy = all(status.get("healthy", False) for status in agent_health.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": agent_health,
        "system": {
            "uptime": "N/A",
            "total_agents": len(agent_health),
            "healthy_agents": sum(1 for s in agent_health.values() if s.get("healthy"))
        }
    }


@app.get("/api/status")
async def system_status():
    """Get comprehensive system status"""
    stats = await state_manager.get_statistics()
    agent_health = await agent_registry.health_check_all()
    
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": agent_registry.list_agents(),
        "statistics": stats,
        "health": agent_health,
    }


# ==================== Agent Management ====================

@app.get("/api/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "agents": agent_registry.list_agents(),
        "total": len(agent_registry.agents)
    }


@app.get("/api/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent info"""
    agent = agent_registry.get_agent(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    metrics = await agent_registry.get_agent_metrics(agent_name)
    health = await agent.health_check()
    
    return {
        "info": agent.get_info(),
        "metrics": metrics,
        "health": health
    }


@app.post("/api/agents/{agent_name}/restart")
async def restart_agent(agent_name: str):
    """Restart an agent"""
    success = await agent_registry.restart_agent(agent_name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found or restart failed")
    
    return {"status": "restarted", "agent": agent_name}


# ==================== Memory Operations ====================

@app.post("/api/memory/learn")
async def learn_pattern(request: Dict[str, Any]):
    """Learn a new pattern for automation"""
    result = await agent_registry.call_agent(
        "memory_agent",
        "learn_pattern",
        pattern_id=request.get("pattern_id"),
        pattern_data=request.get("pattern_data")
    )
    return result


@app.get("/api/memory/patterns")
async def get_patterns():
    """Retrieve all learned patterns"""
    result = await agent_registry.call_agent("memory_agent", "recall_pattern")
    return result


@app.post("/api/memory/solution")
async def store_solution(request: Dict[str, Any]):
    """Store a solution for a problem"""
    result = await agent_registry.call_agent(
        "memory_agent",
        "store_solution",
        problem=request.get("problem"),
        solution=request.get("solution")
    )
    return result


@app.get("/api/memory/solution/{problem}")
async def get_solution(problem: str):
    """Get a known solution"""
    result = await agent_registry.call_agent(
        "memory_agent",
        "get_solution",
        problem=problem
    )
    return result


@app.get("/api/memory/growth")
async def get_growth_metrics():
    """Get system growth and learning metrics"""
    result = await agent_registry.call_agent("memory_agent", "get_growth_metrics")
    return result


# ==================== Issue Management ====================

@app.post("/api/issues/detect")
async def detect_issue(request: Dict[str, Any]):
    """Detect and log a new issue"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "detect_issue",
        issue=request
    )
    return {"issue_id": result, "status": "detected"}


@app.get("/api/issues")
async def list_issues(status: str = None, severity: str = None):
    """List issues with optional filtering"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "list_issues",
        status=status,
        severity=severity
    )
    return result


@app.get("/api/issues/{issue_id}")
async def get_issue(issue_id: str):
    """Get specific issue details"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "get_issue",
        issue_id=issue_id
    )
    return result


@app.get("/api/issues/analysis")
async def analyze_issues():
    """Analyze all issues for patterns"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "analyze_issues"
    )
    return result


@app.post("/api/issues/{issue_id}/status")
async def update_issue_status(issue_id: str, request: Dict[str, Any]):
    """Update issue status"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "update_status",
        issue_id=issue_id,
        status=request.get("status")
    )
    return result


@app.post("/api/issues/{issue_id}/investigating")
async def mark_investigating(issue_id: str):
    """Mark issue as under investigation"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "mark_investigating",
        issue_id=issue_id
    )
    return result


@app.post("/api/issues/{issue_id}/resolved")
async def mark_resolved(issue_id: str, request: Dict[str, Any]):
    """Mark issue as resolved"""
    result = await agent_registry.call_agent(
        "issue_agent",
        "mark_resolved",
        issue_id=issue_id,
        resolution=request.get("resolution", "")
    )
    return result


# ==================== Issue Fixing ====================

@app.post("/api/fix/issue/{issue_id}")
async def fix_issue(issue_id: str, background_tasks: BackgroundTasks):
    """Attempt to fix an issue automatically"""
    result = await agent_registry.call_agent(
        "fixer_agent",
        "fix_issue",
        issue_id=issue_id
    )
    return result


@app.post("/api/fix/all")
async def fix_all_issues(background_tasks: BackgroundTasks):
    """Attempt to fix all open issues"""
    result = await agent_registry.call_agent(
        "fixer_agent",
        "auto_fix_open_issues"
    )
    return result


# ==================== WebSocket ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    ws_connections.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Noahubai system",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                response = await handle_ws_message(message)
                await websocket.send_json(response)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON"
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        if websocket in ws_connections:
            ws_connections.remove(websocket)


async def handle_ws_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming WebSocket message"""
    msg_type = message.get("type")
    
    if msg_type == "ping":
        return {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
    
    elif msg_type == "status":
        stats = await state_manager.get_statistics()
        return {"type": "status", "data": stats}
    
    elif msg_type == "health":
        health = await agent_registry.health_check_all()
        return {"type": "health", "data": health}
    
    else:
        return {"type": "error", "error": f"Unknown message type: {msg_type}"}


# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== Root Endpoint ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the Windows 7 style Noahubai shell."""
    return FRONTEND_FILE.read_text(encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
