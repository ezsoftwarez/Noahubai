"""
Noahubai Comprehensive Documentation
Complete system overview and usage guide
"""

# 🤖 NOAHUBAI - Complete System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Agent Details](#agent-details)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Performance Tuning](#performance-tuning)

---

## System Overview

**Noahubai** is a unified AI application with three core capabilities:

### 🧠 **Continuous Learning & Memory**
- System learns patterns automatically
- Stores solutions for recurring problems
- Builds intelligent knowledge base
- Improves effectiveness over time

### 🔍 **Intelligent Issue Detection & Tracking**
- Detects problems automatically
- Remembers all issues (never forgets)
- Tracks complete lifecycle
- Identifies patterns across failures

### 🔧 **Automated Problem Resolution**
- Applies known solutions
- Learns from successful fixes
- Attempts multiple strategies
- Escalates for manual intervention when needed

---

## Installation

### Windows

1. **Automatic Installation**
   ```cmd
   python setup.py
   # or
   setup.bat
   ```

2. **Manual Installation**
   ```cmd
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run application
   python main.py
   ```

### Linux/macOS

1. **Automatic Installation**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Manual Installation**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run application
   python main.py
   ```

---

## Quick Start

### Start the System

```bash
# Windows
run_noahubai.bat

# Linux/macOS
./run_noahubai.sh
```

### Access the Interface

- **Web Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

### First Actions

1. **Check System Health**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **List Active Agents**
   ```bash
   curl http://localhost:8000/api/agents
   ```

3. **Get System Status**
   ```bash
   curl http://localhost:8000/api/status
   ```

---

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                   Web UI / API Client                    │
├─────────────────────────────────────────────────────────┤
│                   FastAPI Server (8000)                  │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────┬──────────────┬─────────────────┐    │
│  │ Memory Agent  │ Issue Agent  │ Fixer Agent     │    │
│  │  (Learning)   │ (Detection)  │  (Fixing)       │    │
│  └───────────────┴──────────────┴─────────────────┘    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┬──────────────┬──────────────────┐    │
│  │ Event Bus   │ State Manager│ Agent Registry   │    │
│  │ (Pub/Sub)   │ (Storage)    │ (Orchestration) │    │
│  └─────────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Communication Flow

```
User Request
    ↓
API Route
    ↓
Agent Registry
    ↓
Target Agent
    ↓
State Manager (Update) + Event Bus (Publish)
    ↓
WebSocket Broadcast → All Clients
    ↓
Response to Requestor
```

---

## Agent Details

### 🧠 Memory Agent

**Purpose**: Learn patterns, store solutions, enable growth

**Sub-Agents**:
- Pattern Detector
- Solution Keeper
- Growth Calculator

**Key Capabilities**:
- Pattern learning and recall
- Solution storage and retrieval
- Growth metrics calculation
- Knowledge base management

**APIs**:
- `POST /api/memory/learn` - Learn pattern
- `GET /api/memory/patterns` - Get patterns
- `POST /api/memory/solution` - Store solution
- `GET /api/memory/growth` - Get growth metrics

### 🔍 Issue Agent

**Purpose**: Detect, remember, and track all issues

**Sub-Agents**:
- Issue Detector
- Issue Categorizer
- Pattern Analyzer
- Lifecycle Manager

**Key Capabilities**:
- Real-time issue detection
- Automatic categorization
- Pattern analysis
- Lifecycle management

**APIs**:
- `POST /api/issues/detect` - Detect issue
- `GET /api/issues` - List issues
- `GET /api/issues/{id}` - Get details
- `POST /api/issues/{id}/status` - Update status

### 🔧 Fixer Agent

**Purpose**: Automatically fix issues using learned solutions

**Sub-Agents**:
- Solution Applier
- Strategy Engine
- Safety Checker
- Learning Engine

**Key Capabilities**:
- Apply known solutions
- Generate fix strategies
- Validate fixes
- Learn from results

**APIs**:
- `POST /api/fix/issue/{id}` - Fix issue
- `POST /api/fix/all` - Fix all issues

---

## API Reference

### Health & Status

#### System Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "agents": {
    "memory_agent": {"healthy": true, "state": "ready"},
    "issue_agent": {"healthy": true, "state": "ready"},
    "fixer_agent": {"healthy": true, "state": "ready"}
  },
  "system": {
    "total_agents": 3,
    "healthy_agents": 3
  }
}
```

#### System Status
```
GET /api/status
```

### Agent Management

#### List Agents
```
GET /api/agents
```

#### Get Agent Details
```
GET /api/agents/{agent_name}
```

#### Restart Agent
```
POST /api/agents/{agent_name}/restart
```

### Memory Operations

#### Learn Pattern
```
POST /api/memory/learn

Request Body:
{
  "pattern_id": "cache-on-load",
  "pattern_data": {
    "condition": "high_load",
    "action": "enable_cache"
  }
}
```

#### Store Solution
```
POST /api/memory/solution

Request Body:
{
  "problem": "timeout",
  "solution": {
    "steps": [
      {"type": "config", "action": "Increase timeout"},
      {"type": "cache", "action": "Enable caching"}
    ]
  }
}
```

#### Get Growth Metrics
```
GET /api/memory/growth
```

### Issue Management

#### Detect Issue
```
POST /api/issues/detect

Request Body:
{
  "type": "timeout",
  "message": "API request timeout",
  "severity": "warning",
  "context": {"endpoint": "/api/users"}
}
```

#### List Issues
```
GET /api/issues?status=open&severity=error
```

#### Update Issue Status
```
POST /api/issues/{issue_id}/status

Request Body:
{
  "status": "investigating"
}
```

### Issue Fixing

#### Fix Specific Issue
```
POST /api/fix/issue/{issue_id}
```

#### Fix All Open Issues
```
POST /api/fix/all
```

---

## Runtime Defaults

The server currently starts with code-level defaults in `main.py` and `backend/server.py`:

- Host: `0.0.0.0`
- Port: `8000`
- Log level: `info`

There is no active `.env` loader or settings manager API in the runtime path.

---

## Advanced Features

### Pattern Learning

1. System detects successful pattern
2. MemoryAgent learns and stores
3. Future similar situations use pattern
4. Effectiveness improves over time

### Issue Lifecycle

```
DETECTED → INVESTIGATING → RESOLVED
   ↓
  Store
   ↓
  Learn
   ↓
Automate
```

### Automatic Fixing

1. **Known Solution** - Apply stored solution
2. **Pattern Recognition** - Use similar issue fixes
3. **Auto-Analysis** - Generate strategy
4. **Escalation** - Request manual help

### Growth Metrics

- **Growth Score** (0-100): Overall improvement
- **Success Rate**: Percentage successful
- **Resolution Rate**: Issues fixed
- **Knowledge Base**: Patterns and solutions

---

## Troubleshooting

### Agent Not Starting

```bash
# Check logs
tail -f noahubai.log

# Restart agent
curl -X POST http://localhost:8000/api/agents/{agent_name}/restart
```

### Memory Issues

```python
# Clear old patterns
DELETE /api/memory/patterns?older_than=30days

# Check memory usage
GET /api/status
```

### Issue Detection Problems

```bash
# Manual issue detection
POST /api/issues/detect
```

---

## Support & Resources

- **GitHub**: https://github.com/ezsoftwarez/Noahubai
- **Issues**: Open an issue on GitHub
- **Documentation**: See README.md
- **API Docs**: http://localhost:8000/docs

---

## Version History

### v1.0.0 (Current)
- Initial release
- Memory Agent with pattern learning
- Issue Agent with detection and tracking
- Fixer Agent with automatic resolution
- REST API with full documentation
- WebSocket for real-time updates
- Agent lifecycle and health monitoring

---

**Noahubai** - Growing smarter with every issue solved 🧠✨
