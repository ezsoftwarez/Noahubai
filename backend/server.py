"""
Core API Server - FastAPI backend for Noahubai
Handles all agent communication and provides REST/WebSocket interface
"""
import asyncio
import logging
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

logger = logging.getLogger(__name__)

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
    description="Unified AI Application with Memory, Issue Tracking, and Auto-Fixing",
    version="1.0.0",
    lifespan=lifespan
)

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

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "Noahubai",
        "description": "Unified AI Application with Memory, Issue Tracking, and Auto-Fixing",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "agents": "/api/agents",
            "memory": "/api/memory/*",
            "issues": "/api/issues/*",
            "fixing": "/api/fix/*",
            "websocket": "/ws"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
