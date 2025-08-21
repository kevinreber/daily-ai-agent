# 🤖 Daily AI Assistant Agent

An intelligent AI agent that acts as your **personal productivity assistant**, orchestrating tools from your deployed [MCP server](../daily-mcp-server/) to provide comprehensive daily management. Features both **information retrieval** and **action taking** capabilities.

## 🚀 **NEW: Enhanced Calendar Intelligence!**

✨ **Phase 2.1 Foundation** - AI calendar functionality restored and MCP server upgraded with full Calendar CRUD!

🎯 **What makes this special?** This isn't just another chatbot - it's a **production-ready AI assistant** that:

- **✅ FIXED: Calendar Reading** - Now properly reads and displays your real calendar events
- **Creates real calendar events** through conversational AI (ready for update/delete)
- **Orchestrates 8 specialized tools** with intelligent routing
- **Provides smart conflict detection** when scheduling meetings
- **Integrates live APIs** (Google Calendar, OpenWeatherMap, financial markets)
- **Uses LangChain + GPT-4o-mini** for optimal cost/performance
- **Runs in production** with FastAPI backend and CLI interface

## ✨ Enhanced Features

### 🗣️ **Conversational Calendar Management**

- **✅ "What's on my calendar tomorrow?"** → Now properly reads and displays your real events
- **"Schedule lunch with John tomorrow at noon"** → Creates actual Google Calendar event
- **Smart conflict detection** → Warns about overlapping meetings
- **Multi-calendar support** → Target work, personal, family calendars
- **Natural language parsing** → Understands dates, times, and context
- **🔜 Coming Soon**: _"Move my 2pm meeting to 3pm"_ and _"Cancel my gym session"_

### 📊 **Comprehensive Data Access**

- 🌤️ **Real Weather Data** - Live forecasts from OpenWeatherMap
- 💰 **Live Financial Markets** - Real-time stocks & crypto prices
- 📅 **Calendar Integration** - Multi-calendar events with Google Calendar
- ✅ **Smart Todo Management** - Prioritized task lists with filtering
- 🚗 **Commute Information** - Real-time traffic and route data

### 🤖 **Advanced AI Capabilities**

- **Tool Selection Intelligence** - GPT-4o-mini chooses optimal tools
- **Parallel Execution** - Multiple operations simultaneously
- **Context Awareness** - Remembers conversation flow
- **Error Recovery** - Graceful handling of API failures

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) for package management
- OpenAI API key (for conversational features)
- Running MCP server at https://web-production-66f9.up.railway.app

### Installation

```bash
# Clone and setup
git clone <your-repo-url>
cd daily-ai-agent

# Install dependencies
uv sync

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

### Configuration

Create a `.env` file based on `.env.example`:

```bash
# Required for conversational AI
OPENAI_API_KEY=your_openai_api_key_here

# MCP Server (already configured for your deployment)
MCP_SERVER_URL=https://web-production-66f9.up.railway.app

# Customize your preferences
USER_NAME=Kevin
USER_LOCATION=San Francisco
DEFAULT_COMMUTE_ORIGIN=Home
DEFAULT_COMMUTE_DESTINATION=Office
```

### Usage

```bash
# Quick health check
uv run daily-ai-agent health

# Individual tool commands
uv run daily-ai-agent weather
uv run daily-ai-agent todos
uv run daily-ai-agent commute

# Complete morning briefings
uv run daily-ai-agent briefing          # Basic data briefing
uv run daily-ai-agent smart-briefing    # AI-powered conversational briefing

# Natural language conversations
uv run daily-ai-agent chat -m "What's my day looking like?"
uv run daily-ai-agent chat -m "Should I wear a jacket today?"
uv run daily-ai-agent chat -m "Schedule lunch with John tomorrow at 1pm"  # 🆕 Calendar creation!
uv run daily-ai-agent chat              # Interactive chat mode

# Demo all features
uv run daily-ai-agent demo
```

### 🚀 Try It Now (Quick Start)

```bash
# 1. Clone and setup
git clone <your-repo> && cd daily-ai-agent
uv sync

# 2. Add your OpenAI API key to .env
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-key-here

# 3. Test the connection
uv run daily-ai-agent health

# 4. Try the AI features!
uv run daily-ai-agent smart-briefing
uv run daily-ai-agent chat -m "What's my day like?"
```

## 📋 Example Output

### 🤖 AI-Powered Smart Briefing

```bash
$ uv run daily-ai-agent smart-briefing

🤖 Generating your intelligent morning briefing...

╭───────────────────────────────────────── 🌅 AI Morning Briefing ─────────────────────────────────────────╮
│ Good morning, Kevin! Here's your complete morning briefing:                                              │
│                                                                                                          │
│ 🌤️ **Weather**: It's a lovely day with scattered clouds and a pleasant temperature of **77.4°F**. Perfect │
│ for getting out and about!                                                                               │
│                                                                                                          │
│ 📅 **Calendar**: You have **no events** scheduled for today, so it looks like you have a free day ahead! │
│                                                                                                          │
│ ✅ **Todos**: You have **3 pending tasks** to tackle. Let's make sure to get those done!                 │
│                                                                                                          │
│ 🚗 **Commute**: Since you have no events today, there's no commute information needed for the office.    │
│                                                                                                          │
│ 💰 **Markets**: 7 instruments tracked | 📈 4 gaining | 📉 3 declining | 🏆 Best: BTC (+4.2%)           │
│                                                                                                          │
│ Looks like you have a great day ahead with plenty of time to focus on your tasks! Let me know if you     │
│ need help with anything specific.                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 💬 Natural Language Conversations

```bash
$ uv run daily-ai-agent chat -m "What's my day looking like?"

You: What's my day looking like?
🤖 Thinking...
Assistant: Here's your morning briefing, Kevin:

🌤️ **Weather**: Scattered Clouds - 77.4°F
📅 **Calendar**: 0 events today
✅ **Todos**: 3 pending tasks
🚗 **Commute**: N/A to office
💰 **Markets**: 7 instruments tracked | 📈 4 gaining | 📉 3 declining | 🏆 Best: BTC (+4.2%)

Let me know if you need help with anything specific!

$ uv run daily-ai-agent chat -m "Should I wear a jacket today?"

You: Should I wear a jacket today?
🤖 Thinking...
Assistant: Today in San Francisco, the weather is expected to be warm with a high of 77.4°F and a low of 56.6°F. Since it's a bit on the warmer side, you might not need a jacket, but it could be a good idea to have one handy for the cooler morning or evening.

$ uv run daily-ai-agent chat -m "Schedule lunch with John tomorrow at 1pm"

You: Schedule lunch with John tomorrow at 1pm
🤖 Thinking...
Assistant: ✅ **Event Created Successfully!**

I've created a lunch meeting for you:
- **Title**: Lunch with John
- **Time**: Tomorrow, January 16th, 1:00 PM - 2:00 PM
- **Calendar**: Primary
- **Event ID**: abc123xyz
- **URL**: https://calendar.google.com/calendar/event?eid=abc123xyz

✅ **No conflicts detected** - your calendar is free at that time!

The event has been added to your Google Calendar and John will receive an invitation.

$ uv run daily-ai-agent chat -m "How's Microsoft stock doing?"

You: How's Microsoft stock doing?
🤖 Thinking...
Assistant: The current price of Microsoft (MSFT) is $522.04, up by $1.20 (+0.2%). Looking good with a slight upward trend today!
```

### 📊 Individual Tool Output

```bash
# Weather with real OpenWeatherMap data
$ uv run daily-ai-agent weather

  🌤️ Weather for San Francisco, US
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Metric        ┃ Value            ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ High          │ 77.4°F           │
│ Low           │ 56.6°F           │
│ Precipitation │ 0%               │
│ Summary       │ Scattered Clouds │
│ Date          │ 2025-08-11       │
└───────────────┴──────────────────┘

# Todo management with priorities
$ uv run daily-ai-agent todos

                             ✅ Work Todos
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Task                      ┃ Priority ┃ Due Date                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Review quarterly reports  │ high     │ Tue, 12 Aug 2025 06:24:57 GMT │
│ Code review for PR #123   │ medium   │ Mon, 11 Aug 2025 06:24:57 GMT │
│ Plan sprint retrospective │ medium   │ Sat, 16 Aug 2025 06:24:57 GMT │
└───────────────────────────┴──────────┴───────────────────────────────┘
📊 Total: 3 items, 3 pending

# Financial data with real market prices
$ uv run daily-ai-agent chat -m "Show me MSFT, BTC, and ETH prices"

You: Show me MSFT, BTC, and ETH prices
🤖 Thinking...
Assistant: Here's the latest financial update:

- **Microsoft Corporation (MSFT)**: $522.04 (+$1.20, +0.2%)
- **Bitcoin (BTC)**: $119,483.00 (+$961.16, +0.8%)
- **Ethereum (ETH)**: $4,282.23 (+$57.58, +1.3%)

Let me know if you need anything else!

# Health check
$ uv run daily-ai-agent health
✅ MCP Server is healthy!
```

## 🏗️ Architecture

```
┌─────────────────────┐    HTTP/REST    ┌──────────────────────┐
│   AI Agent Layer   │ ──────────────> │   MCP Server         │
│   (This Project)   │                 │   (Railway Deployed) │
│                     │                 │                      │
│ • FastAPI Server    │                 │ • 6 Tools (5R + 1W)  │
│ • CLI Interface     │                 │ • Weather API ✅      │
│ • Tool Orchestrator │                 │ • Financial API ✅    │
│ • LangChain Agent   │                 │ • Calendar R/W ✅     │
│ • GPT-4o-mini       │                 │ • Todos (Mock) 🔄     │
│                     │                 │ • Mobility API ✅     │
└─────────────────────┘                 └──────────────────────┘
```

## 🔧 Development

### Project Structure

```
daily-ai-agent/
├── src/daily_ai_agent/
│   ├── __init__.py              # Package entry point
│   ├── main.py                  # CLI interface
│   ├── agent/                   # AI orchestration logic
│   ├── services/
│   │   ├── mcp_client.py        # MCP server HTTP client
│   │   └── llm.py              # OpenAI integration (coming)
│   ├── models/
│   │   ├── config.py           # Settings management
│   │   └── schemas.py          # Data models
│   └── utils/                  # Helpers and formatters
├── tests/                      # Test suite
├── examples/                   # Demo scripts
├── requirements.txt           # Dependencies
└── pyproject.toml            # Project configuration
```

### Running Tests

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=daily_ai_agent
```

### Add New Commands

```python
# In src/daily_ai_agent/main.py
@app.command()
def my_command():
    """Add your custom command here."""
    # Your logic here
```

## 🎯 Available Commands

| Command                   | Description                        | Example                                          |
| ------------------------- | ---------------------------------- | ------------------------------------------------ |
| `health`                  | Check MCP server connectivity      | `uv run daily-ai-agent health`                   |
| `weather [location]`      | Get weather forecast               | `uv run daily-ai-agent weather "New York"`       |
| `todos [bucket]`          | List todo items                    | `uv run daily-ai-agent todos work`               |
| `commute [origin] [dest]` | Get commute info                   | `uv run daily-ai-agent commute`                  |
| `briefing [date]`         | Basic morning briefing             | `uv run daily-ai-agent briefing`                 |
| `smart-briefing`          | AI-powered conversational briefing | `uv run daily-ai-agent smart-briefing`           |
| `chat -m "message"`       | Natural language conversation      | `uv run daily-ai-agent chat -m "Schedule lunch"` |
| `chat`                    | Interactive chat mode              | `uv run daily-ai-agent chat`                     |
| `demo`                    | Run feature demonstration          | `uv run daily-ai-agent demo`                     |

### 🆕 **Calendar Creation Examples** (via chat)

- `chat -m "Schedule lunch with John tomorrow at 1pm"`
- `chat -m "Book dentist appointment next Tuesday at 3pm"`
- `chat -m "Create team meeting Friday 2-3pm in Conference Room A"`
- `chat -m "Set up workout session this weekend"`

## 🚀 Roadmap

### ✅ **Phase 1.5 Complete** (Calendar Creation)

- [x] MCP server integration with 6 tools
- [x] Calendar event creation via natural language
- [x] Smart conflict detection for scheduling
- [x] Multi-calendar support (Primary, Runna, Family)
- [x] LangChain + GPT-4o-mini tool orchestration
- [x] FastAPI server + CLI interface
- [x] Real Google Calendar integration
- [x] Production deployment (Railway + Vercel)

### 🔄 **Phase 2 In Progress** (Enhanced Intelligence)

- [ ] Smart scheduling - AI suggests optimal meeting times
- [ ] Calendar update/delete operations
- [ ] Natural language time parsing ("next Tuesday", "in 2 hours")
- [ ] Conversation memory and context
- [ ] Todo write operations (create, update, complete)

### 🔮 **Future Phases** (Advanced Features)

- [ ] Multi-tenancy and user management
- [ ] Proactive notifications and reminders
- [ ] Voice integration (speech-to-text)
- [ ] Team collaboration features
- [ ] Mobile app integration
- [ ] Slack/Teams bot integration

## 🤝 Integration

### With MCP Server

This agent connects to your deployed MCP server at:

- **Health**: `GET /health`
- **Tools**: `POST /tools/{tool_name}`
- **List**: `GET /tools`

### With Frontend (Planned)

The agent will expose REST endpoints for:

- **Chat**: `POST /chat`
- **Briefing**: `GET /briefing`
- **Tools**: `GET /tools/{tool_name}`

## 📚 Related Projects

- **[MCP Server](../daily-mcp-server/)** - Backend tools and APIs
- **Morning Routine Frontend** - Web interface (coming soon)

## 🛡️ Security

- **Environment variables** for all API keys
- **No sensitive data** in git repository
- **Secure HTTP** connections to external APIs
- **Input validation** for all user inputs

## 📝 License

MIT License - See LICENSE file for details

## 🙋‍♂️ Support

For questions or issues:

1. Check the [AI Agent Strategy](./AI_AGENT_STRATEGY.md) document
2. Review the [MCP Server documentation](../daily-mcp-server/README.md)
3. Create an issue in this repository

---

**Happy morning routines! 🌅**
