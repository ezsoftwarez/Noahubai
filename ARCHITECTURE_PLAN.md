# NOAHUBAI - Unified AI Application Architecture Plan

## Product & monetization

**Primary product:** [AI Hub](AI%20HUB%20oVerk1LL/) — local Cursor bridge and daily-run workspace.  
**Engine:** Noahubai backend (this repo's agents + FastAPI).  
**Model:** Open-core — Free local core; Pro/Team workflow features via entitlements.

| Doc | Purpose |
|-----|---------|
| [docs/PRODUCT.md](docs/PRODUCT.md) | Product definition and audience |
| [docs/PRICING.md](docs/PRICING.md) | Free / Pro / Team feature split |
| [backend/entitlements.py](backend/entitlements.py) | Plan tiers and feature matrix |
| [backend/middleware.py](backend/middleware.py) | API entitlement enforcement |

Experiments (job/freelance demos) are **not** the core product — see [docs/experiments/](docs/experiments/).

## 🎯 Vision
Single, monolithic AI application combining browser, AI Hub, and multiple independent intelligent agents working in parallel with zero coupling.

---

## 📋 Project Structure

```
noahubai/
├── core/                          # Core engine & orchestration
│   ├── agent_framework.py          # Agent base class & lifecycle
│   ├── agent_registry.py           # Agent discovery & management
│   ├── event_bus.py                # Pub/Sub for async messaging
│   ├── config_manager.py           # Global config & secrets
│   ├── state_manager.py            # Shared state with isolation
│   └── utils.py                    # Helpers & common functions
│
├── agents/                         # Independent agent modules (DETACHED)
│   ├── __init__.py
│   ├── base_agent.py               # Agent interface
│   │
│   ├── browser_agent/              # Web browsing & scraping
│   │   ├── __init__.py
│   │   ├── browser_core.py
│   │   ├── tab_vault.py
│   │   ├── ad_blocker.py
│   │   ├── security_checker.py
│   │   └── requirements.txt
│   │
│   ├── nlp_agent/                  # Natural language processing
│   │   ├── __init__.py
│   │   ├── text_processor.py
│   │   ├── sentiment_analysis.py
│   │   ├── intent_classifier.py
│   │   └── requirements.txt
│   │
│   ├── data_agent/                 # Data processing & analysis
│   │   ├── __init__.py
│   │   ├── data_processor.py
│   │   ├── data_analyzer.py
│   │   ├── database.py
│   │   └── requirements.txt
│   │
│   ├── automation_agent/           # Task automation
│   │   ├── __init__.py
│   │   ├── task_scheduler.py
│   │   ├── workflow_executor.py
│   │   ├── macro_recorder.py
│   │   └── requirements.txt
│   │
│   ├── reasoning_agent/            # Complex reasoning & problem-solving
│   │   ├── __init__.py
│   │   ├── llm_interface.py
│   │   ├── prompt_manager.py
│   │   ├── memory_system.py
│   │   └── requirements.txt
│   │
│   ├── search_agent/               # Smart search & retrieval
│   │   ├── __init__.py
│   │   ├── search_engine.py
│   │   ├── indexer.py
│   │   ├── result_ranker.py
│   │   └── requirements.txt
│   │
│   ├── code_agent/                 # Code analysis & generation
│   │   ├── __init__.py
│   │   ├── code_analyzer.py
│   │   ├── code_generator.py
│   │   ├── language_parser.py
│   │   └── requirements.txt
│   │
│   └── monitoring_agent/           # System health & performance
│       ├── __init__.py
│       ├── system_monitor.py
│       ├── log_aggregator.py
│       ├── alert_manager.py
│       └── requirements.txt
│
├── backend/                        # API & Bridge Server
│   ├── __init__.py
│   ├── server.py                   # Flask/FastAPI main server
│   ├── api_routes.py               # REST endpoints
│   ├── websocket_handler.py        # Real-time communication
│   ├── middleware.py               # Auth, logging, rate-limiting, entitlements
│   ├── entitlements.py             # Free/Pro/Team plans and license keys
│   ├── db/                         # Database layer
│   │   ├── models.py
│   │   ├── orm_config.py
│   │   └── migrations/
│   └── requirements.txt
│
├── frontend/                       # Web UI
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx                 # Main React component
│   │   ├── components/
│   │   │   ├── AgentDashboard.jsx
│   │   │   ├── AgentControl.jsx
│   │   │   ├── Browser.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DataViewer.jsx
│   │   │   ├── TaskScheduler.jsx
│   │   │   └── SystemStatus.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── websocket.js
│   │   │   └── agent_controller.js
│   │   ├── styles/
│   │   │   ├── main.css
│   │   │   └── themes.css
│   │   └── utils/
│   │       ├── formatters.js
│   │       ├── validators.js
│   │       └── helpers.js
│   ├── package.json
│   └── .env.example
│
├── config/                         # Configuration
│   ├── default.yml
│   ├── development.yml
│   ├── production.yml
│   ├── agents_config.yml           # Agent-specific settings
│   └── .env.example
│
├── tests/                          # Testing suite
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_core.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_agent_communication.py
│   │   ├── test_event_bus.py
│   │   └── test_api.py
│   └── conftest.py
│
├── scripts/                        # Utility scripts
│   ├── setup.py
│   ├── run.py                      # Main entry point
│   ├── agent_manager.py            # Start/stop agents
│   ├── db_init.py                  # Database initialization
│   └── health_check.py
│
├── docs/                           # Documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── AGENT_DEVELOPMENT.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── docker/                         # Containerization
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── .github/
│   └── workflows/                  # CI/CD pipelines
│       ├── test.yml
│       ├── build.yml
│       └── deploy.yml
│
├── requirements.txt                # Root dependencies
├── setup.py                        # Package setup
├── pyproject.toml                  # Modern Python packaging
├── .gitignore
└── README.md                       # Main documentation

```

---

## 🤖 Agent Specifications

### 1. **Browser Agent** (Headless Web Control)
- Manages web browsing, tab management, scraping
- Independent lifecycle: spawn/kill without affecting others
- **Functions:**
  - `navigate(url)` - Navigate to URL
  - `scrape(selector)` - CSS selector scraping
  - `take_screenshot()` - Capture page
  - `extract_metadata()` - Get page info
  - `block_ads()` - Run ad-blocker rules
  - `check_security(url)` - VirusTotal checks
  - **Communication:** Event bus (no direct calls)

### 2. **NLP Agent** (Language Understanding)
- Text processing, sentiment, intent detection
- Pure processing — stateless
- **Functions:**
  - `parse_text(text)` - Tokenize & analyze
  - `get_sentiment(text)` - Sentiment score
  - `classify_intent(text)` - Intent extraction
  - `summarize(text, max_len)` - Text summarization
  - `extract_entities(text)` - Named entity recognition
  - **Communication:** Request/response via event bus

### 3. **Data Agent** (Processing & Storage)
- Database operations, analytics, caching
- Thread-safe database access
- **Functions:**
  - `store(key, data)` - Persist data
  - `retrieve(key, query)` - Fetch with filtering
  - `analyze(dataset)` - Statistical analysis
  - `cache(key, value, ttl)` - Cache management
  - `export(format)` - Data export (CSV, JSON)
  - **Communication:** Isolated database; pub/sub for updates

### 4. **Automation Agent** (Task Execution)
- Workflow orchestration, scheduling, macros
- Parallel task execution with isolation
- **Functions:**
  - `schedule_task(spec, cron)` - Schedule execution
  - `execute_workflow(steps)` - Run workflow
  - `record_macro(actions)` - Record user actions
  - `playback_macro(name)` - Replay recorded actions
  - `cancel_task(id)` - Stop execution
  - **Communication:** Task queue + event bus

### 5. **Reasoning Agent** (AI/LLM Interface)
- Advanced problem-solving, conversation, context management
- Memory & conversation history
- **Functions:**
  - `query(prompt, context)` - LLM inference
  - `reason(problem)` - Multi-step reasoning
  - `generate_code(description)` - Code generation
  - `answer_question(q)` - QA
  - `remember(key, fact)` - Store in memory
  - **Communication:** REST → LLM + state bus

### 6. **Search Agent** (Information Retrieval)
- Full-text search, indexing, ranking
- Powered by browser + data agents
- **Functions:**
  - `index_content(text, source)` - Index for search
  - `search(query, filters)` - Execute search
  - `rank_results(results)` - Smart ranking
  - `get_suggestions(prefix)` - Auto-complete
  - **Communication:** Event bus + database

### 7. **Code Agent** (Development Support)
- Code analysis, generation, debugging
- Language-aware parsing
- **Functions:**
  - `analyze_code(code, lang)` - AST analysis
  - `generate_code(spec, lang)` - Generate from spec
  - `find_errors(code)` - Linting
  - `explain_code(code)` - Code explanation
  - `refactor(code)` - Suggest improvements
  - **Communication:** Stateless; results via event bus

### 8. **Monitoring Agent** (System Health)
- Real-time performance tracking, logging, alerting
- Watches all other agents
- **Functions:**
  - `get_status()` - System health
  - `get_agent_metrics(agent_id)` - Agent performance
  - `get_logs(filters)` - Log retrieval
  - `trigger_alert(level, msg)` - Alert system
  - `get_resource_usage()` - CPU/Memory/Disk
  - **Communication:** Read-only subscriptions

---

## 🔌 Communication Architecture (DETACHED Agents)

### Event Bus (Pub/Sub)
```python
# Agents publish events, others subscribe
event_bus.publish("browser.page_loaded", {url, content, title})
event_bus.subscribe("nlp.sentiment", callback)

# No direct coupling
```

### Request/Response (Light Coupling)
```python
# For synchronous operations with timeout
result = agent_registry.call("search_agent.find", query="ai", timeout=5s)
```

### Task Queue (Async Heavy Work)
```python
# Long-running tasks
task_id = automation_agent.schedule("report_generation", params)
status = automation_agent.get_task_status(task_id)
```

### State Isolation
```python
# Each agent has private state + shared cache
agent_state = state_manager.get_agent_state("browser_agent")
shared_cache = state_manager.get_cache("global")
```

---

## 🎮 Frontend Unified Interface

### Main Dashboard
- **Agent Status Panel** — Real-time health of all agents
- **Unified Search Bar** — Routes to search agent
- **Chat Interface** — Talks to reasoning agent
- **Browser Viewport** — Browser agent output
- **Task Manager** — Automation agent tasks
- **Data Viewer** — Data agent results
- **System Monitor** — Monitoring agent metrics

### Real-time Updates (WebSocket)
- Agent status changes
- Task completion notifications
- Incoming chat messages
- System alerts

---

## 🚀 Startup & Lifecycle

### Main Entry Point (`scripts/run.py`)
```
1. Load configuration
2. Initialize core (event bus, state manager, registry)
3. Spin up backend server
4. Discover & load all agents
5. Start each agent in isolated thread/process
6. Open web UI
7. Monitor agent health
8. Graceful shutdown (stop agents → flush state → close DB)
```

### Agent Lifecycle
```
IDLE → STARTING → READY → WORKING → READY/ERROR → STOPPING → STOPPED

Each agent manages its own lifecycle.
Registry monitors and can restart failed agents.
```

---

## 💾 Data Flow

```
User Input (Web UI)
    ↓
API Route Handler
    ↓
Agent Router (which agent to call?)
    ↓
[AGENT QUEUE]
    ↓
Agent Processing (Isolated)
    ↓
[STATE MANAGER] - Update shared state
[EVENT BUS] - Notify subscribers
    ↓
Response → User
    ↓
WebSocket → Live Updates
```

---

## 🔒 Isolation & Safety

| Isolation Level | Mechanism | Benefit |
|---|---|---|
| **Code** | Separate modules/imports | Easy to maintain & test |
| **Process** | Optional multiprocessing | Fault isolation |
| **Memory** | Private state dicts | No cross-contamination |
| **Database** | Transaction isolation | Concurrent access |
| **Network** | Agent registry RPC | Controlled communication |
| **Permissions** | Config-based ACL | Security boundaries |

---

## 🧪 Testing Strategy

```
├── Unit Tests
│   ├── Test each agent independently
│   ├── Mock external dependencies
│   └── Run in parallel
│
├── Integration Tests
│   ├── Test agent-to-agent communication
│   ├── Test event bus pub/sub
│   ├── Test API routes
│   └── Test database transactions
│
└── E2E Tests
    ├── Full user workflows
    ├── Multi-agent scenarios
    └── Performance benchmarks
```

---

## 📦 Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| **Core** | Python 3.10+ | Performance + ML ecosystem |
| **Backend** | FastAPI + Uvicorn | Async, WebSocket support, modern |
| **Frontend** | React + Redux | State management, reactive UI |
| **Database** | PostgreSQL | Scalable, ACID, JSON support |
| **Cache** | Redis | Fast shared state, pub/sub |
| **Broker** | Celery/RabbitMQ | Distributed task queue |
| **Browser** | Playwright/Selenium | Headless automation |
| **LLM** | OpenAI API / Local LLama | Reasoning agent |
| **Search** | Elasticsearch | Full-text indexing |
| **Monitoring** | Prometheus + Grafana | Metrics & visualization |
| **Containerization** | Docker + Docker Compose | Deployment consistency |

---

## 🎯 Development Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure
- [ ] Implement core (event bus, registry, state manager)
- [ ] Create agent base class & interfaces
- [ ] Implement browser agent (minimal)
- [ ] Implement NLP agent
- [ ] Basic API routes

### Phase 2: Intelligence (Week 3-4)
- [ ] Reasoning agent (LLM integration)
- [ ] Search agent
- [ ] Data agent with DB
- [ ] Automation agent
- [ ] Event bus inter-agent communication

### Phase 3: Features (Week 5-6)
- [ ] Code agent
- [ ] Monitoring agent
- [ ] Frontend dashboard
- [ ] WebSocket real-time updates
- [ ] Task scheduler UI

### Phase 4: Polish (Week 7-8)
- [ ] Comprehensive testing
- [ ] Documentation
- [ ] Docker setup
- [ ] Performance optimization
- [ ] Security hardening
- [ ] CI/CD pipeline

---

## 🔑 Key Design Principles

1. **Independence** — Agents operate without knowledge of each other
2. **Async-First** — Non-blocking communication via event bus
3. **Stateless Logic** — Business logic in agents, state in manager
4. **Fail-Safe** — One agent crash doesn't kill the system
5. **Observable** — Every agent action is logged & monitored
6. **Scalable** — Can run agents on different servers
7. **Extensible** — Add new agents without modifying core

---

## 📊 Success Metrics

- ✅ All agents running independently with < 1s response time
- ✅ Zero cascading failures
- ✅ 95%+ uptime for core system
- ✅ < 500MB base memory footprint
- ✅ WebSocket updates within 100ms
- ✅ Full test coverage (unit + integration)
- ✅ Complete API documentation
- ✅ Deployable in single Docker command

---

## 🚀 Deployment

### Local Development
```bash
./scripts/run.py --dev --agents=all
```

### Docker Production
```bash
docker-compose up -d
```

### Agent Scaling
```bash
# Run specific agents on different servers
python -m agents.browser_agent --port 8001
python -m agents.reasoning_agent --port 8002
# Central coordinator connects via registry
```

---

This architecture ensures **zero coupling** between agents while maintaining **unified control** through the core framework and API layer.
