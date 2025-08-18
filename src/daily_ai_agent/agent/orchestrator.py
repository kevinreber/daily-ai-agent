"""Main agent orchestrator that handles conversations and tool selection."""

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, Any
from loguru import logger

from .tools import get_all_tools
from ..models.config import get_settings
from ..services.llm import LLMService


class AgentOrchestrator:
    """Main orchestrator for the AI agent."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm_service = LLMService()
        self.tools = get_all_tools()
        
        # Initialize LangChain agent if OpenAI is available
        if self.settings.openai_api_key:
            self._init_langchain_agent()
        else:
            self.agent = None
            logger.warning("No OpenAI API key - conversational features disabled")
    
    def _init_langchain_agent(self):
        """Initialize the LangChain agent with tools."""
        try:
            # Create the LLM
            llm = ChatOpenAI(
                api_key=self.settings.openai_api_key,
                model="gpt-4o-mini",
                temperature=0.1
            )
            
            # Create the prompt template
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_day = datetime.now().strftime("%A, %B %d, %Y")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are {self.settings.user_name}'s personal morning assistant. 
You help with their daily routine by providing weather, calendar, todo, and commute information.

IMPORTANT: Today's date is {current_date} ({current_day}). When users ask about "today", "this morning", "my schedule", etc., use this date: {current_date}.

User preferences:
- Name: {self.settings.user_name}
- Location: {self.settings.user_location}
- Default commute: {self.settings.default_commute_origin} to {self.settings.default_commute_destination}

You have access to these tools:
- get_weather: Get weather forecasts
- get_calendar: Get calendar events for a single date (use YYYY-MM-DD format, today is {current_date})
- get_calendar_range: Get calendar events for a date range (MUCH more efficient for week queries)
- get_todos: Get todo/task lists
- get_commute: Get travel information
- get_morning_briefing: Get complete morning summary

IMPORTANT: For week/multi-day queries, ALWAYS use get_calendar_range instead of multiple get_calendar calls. 
Use get_calendar_range when users ask about "this week", "next week", "upcoming days", or any date range.

Be helpful, concise, and friendly. When users ask general questions like "What's my day like?", 
use the morning briefing tool. For specific questions, use the appropriate individual tools.

IMPORTANT: When users ask about "work schedule" or "work meetings", they mean their job/professional calendar.
Currently only personal calendar, Runna (fitness), and Family calendars are available via API.
If asked about work meetings specifically, explain that work calendar integration requires additional setup."""),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Create the agent
            agent = create_tool_calling_agent(llm, self.tools, prompt)
            self.agent = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            logger.info("LangChain agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LangChain agent: {e}")
            self.agent = None
    
    async def chat(self, user_input: str) -> str:
        """
        Handle a conversational input from the user.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            AI assistant response
        """
        if not self.agent:
            return "I need an OpenAI API key to have conversations. Try the specific commands like 'briefing' or 'weather' instead!"
        
        try:
            logger.info(f"Processing user input: {user_input}")
            
            # Use the agent to process the input
            result = await self.agent.ainvoke({"input": user_input})
            response = result.get("output", "I'm not sure how to help with that.")
            
            logger.info("Successfully generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def get_smart_briefing(self) -> str:
        """
        Get an AI-generated morning briefing.
        
        Returns:
            Natural language morning briefing
        """
        try:
            # Get all the morning data
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Use the morning briefing tool through the agent if available
            if self.agent:
                result = await self.agent.ainvoke({
                    "input": "Give me my complete morning briefing with weather, calendar, todos, and commute information. Make it conversational and highlight the most important things."
                })
                return result.get("output", "Error generating briefing")
            else:
                # Fallback to direct tool call
                from ..services.mcp_client import MCPClient
                client = MCPClient()
                data = await client.get_all_morning_data(today)
                return await self.llm_service.generate_morning_briefing(data)
                
        except Exception as e:
            logger.error(f"Error generating smart briefing: {e}")
            return f"Error generating briefing: {str(e)}"
    
    def is_conversational(self) -> bool:
        """Check if conversational features are available."""
        return self.agent is not None
