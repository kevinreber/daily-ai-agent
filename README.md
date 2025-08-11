# 🤖 Morning Routine AI Agent

An intelligent AI agent that provides personalized morning briefings by orchestrating tools from your deployed [MCP server](../daily-mcp-server/). Combines **real weather data** with **calendar, todos, and commute information** to create comprehensive morning summaries.

🎯 **What makes this special?** This isn't just another chatbot - it's a **production-ready AI system** that demonstrates:

- **Real API integration** (OpenWeatherMap) with **realistic mock data**
- **LangChain tool orchestration** with **parallel execution** for speed
- **Natural language conversations** that **intelligently select tools**
- **Beautiful CLI interface** with **structured output**
- **Proper error handling** and **graceful fallbacks**

## ✨ Features

- 🌤️ **Real Weather Data** - Live forecasts from OpenWeatherMap
- ✅ **Smart Todo Management** - Prioritized task lists
- 📅 **Calendar Integration** - Today's events and meetings
- 🚗 **Commute Information** - Travel time and route suggestions
- ⚡ **Lightning Fast** - Parallel tool execution (~3 seconds)
- 🎨 **Beautiful CLI** - Rich formatting with tables and panels
- 🤖 **AI-Powered** - Natural language conversations with OpenAI

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

Let me know if you need help with anything specific!

$ uv run daily-ai-agent chat -m "Should I wear a jacket today?"

You: Should I wear a jacket today?
🤖 Thinking...
Assistant: Today in San Francisco, the weather is expected to be warm with a high of 77.4°F and a low of 56.6°F. Since it's a bit on the warmer side, you might not need a jacket, but it could be a good idea to have one handy for the cooler morning or evening.
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
│ • CLI Interface     │                 │ • Weather API        │
│ • Tool Orchestrator │                 │ • Calendar (Mock)    │
│ • LangChain Agent   │                 │ • Todos (Mock)       │
│ • OpenAI ChatGPT    │                 │ • Mobility (Mock)    │
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
| `chat -m "message"`       | Natural language conversation      | `uv run daily-ai-agent chat -m "What's urgent?"` |
| `chat`                    | Interactive chat mode              | `uv run daily-ai-agent chat`                     |
| `demo`                    | Run feature demonstration          | `uv run daily-ai-agent demo`                     |

## 🚀 Roadmap

### ✅ Completed

- [x] MCP server integration
- [x] Parallel tool execution
- [x] Rich CLI interface
- [x] Error handling and logging
- [x] Health checks
- [x] Natural language conversations with OpenAI
- [x] LangChain tool selection and orchestration
- [x] AI-powered morning briefings

### 🔄 In Progress

- [ ] Conversation memory and context
- [ ] Learning from user preferences

### 🔮 Planned

- [ ] Web API for frontend integration
- [ ] Slack bot integration
- [ ] Proactive notifications
- [ ] Learning user preferences
- [ ] Mobile app support

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
