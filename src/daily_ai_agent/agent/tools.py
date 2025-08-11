"""LangChain tools that wrap MCP server calls."""

from langchain_core.tools import BaseTool
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

from ..services.mcp_client import MCPClient
from ..models.config import get_settings


class WeatherInput(BaseModel):
    """Input schema for weather tool."""
    location: str = Field(description="Location to get weather for (city, state/country)")
    when: str = Field(default="today", description="When to get weather: 'today' or 'tomorrow'")


class CalendarInput(BaseModel):
    """Input schema for calendar tool."""
    date: str = Field(description="Date to get events for in YYYY-MM-DD format")


class TodoInput(BaseModel):
    """Input schema for todo tool.""" 
    bucket: str = Field(default="work", description="Todo bucket: 'work', 'home', 'errands', or 'personal'")


class CommuteInput(BaseModel):
    """Input schema for commute tool."""
    origin: str = Field(description="Starting location")
    destination: str = Field(description="Destination location")
    mode: str = Field(default="driving", description="Transport mode: 'driving', 'transit', 'bicycling', 'walking'")


class WeatherTool(BaseTool):
    """Tool to get weather forecasts."""
    
    name: str = "get_weather"
    description: str = "Get weather forecast for a location. Use this when users ask about weather, temperature, or conditions."
    args_schema: Type[BaseModel] = WeatherInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, location: str, when: str = "today") -> str:
        """Get weather forecast."""
        try:
            client = self._get_mcp_client()
            data = await client.get_weather(location, when)
            return f"Weather for {data.get('location', location)}: {data.get('summary', 'N/A')}, High: {data.get('temp_hi', 'N/A')}°F, Low: {data.get('temp_lo', 'N/A')}°F, Precipitation: {data.get('precip_chance', 0)}%"
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def _run(self, location: str, when: str = "today") -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(location, when))


class CalendarTool(BaseTool):
    """Tool to get calendar events."""
    
    name: str = "get_calendar"
    description: str = "Get calendar events for a specific date. Use when users ask about meetings, appointments, or schedule."
    args_schema: Type[BaseModel] = CalendarInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, date: str) -> str:
        """Get calendar events."""
        try:
            client = self._get_mcp_client()
            data = await client.get_calendar_events(date)
            events = data.get('events', [])
            total = data.get('total_events', 0)
            
            if total == 0:
                return f"No events scheduled for {date}"
            
            event_summaries = []
            for event in events[:3]:  # Show max 3 events
                event_summaries.append(f"- {event.get('title', 'N/A')} at {event.get('time', 'N/A')}")
            
            result = f"{total} events on {date}:\\n" + "\\n".join(event_summaries)
            if total > 3:
                result += f"\\n... and {total - 3} more events"
            
            return result
        except Exception as e:
            return f"Error getting calendar: {str(e)}"
    
    def _run(self, date: str) -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(date))


class TodoTool(BaseTool):
    """Tool to get todo items."""
    
    name: str = "get_todos"
    description: str = "Get todo/task items from different buckets. Use when users ask about tasks, todos, or what they need to do."
    args_schema: Type[BaseModel] = TodoInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, bucket: str = "work") -> str:
        """Get todo items."""
        try:
            client = self._get_mcp_client()
            data = await client.get_todos(bucket)
            items = data.get('items', [])
            pending = data.get('pending_count', 0)
            
            if pending == 0:
                return f"No pending {bucket} tasks"
            
            # Show high priority items first
            high_priority = [item for item in items if item.get('priority') == 'high']
            other_items = [item for item in items if item.get('priority') != 'high']
            
            summaries = []
            
            # Add high priority items first
            for item in high_priority[:2]:
                summaries.append(f"🔥 HIGH: {item.get('title', 'N/A')}")
            
            # Add other items
            for item in other_items[:3]:
                priority = item.get('priority', 'medium').upper()
                summaries.append(f"• {priority}: {item.get('title', 'N/A')}")
            
            result = f"{pending} pending {bucket} tasks:\\n" + "\\n".join(summaries)
            if len(items) > 5:
                result += f"\\n... and {len(items) - 5} more tasks"
            
            return result
        except Exception as e:
            return f"Error getting todos: {str(e)}"
    
    def _run(self, bucket: str = "work") -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(bucket))


class CommuteTool(BaseTool):
    """Tool to get commute information."""
    
    name: str = "get_commute"
    description: str = "Get commute/travel information between locations. Use when users ask about travel time, routes, or transportation."
    args_schema: Type[BaseModel] = CommuteInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, origin: str, destination: str, mode: str = "driving") -> str:
        """Get commute information."""
        try:
            client = self._get_mcp_client()
            data = await client.get_commute(origin, destination, mode)
            return f"Commute from {origin} to {destination} ({mode}): {data.get('duration', 'N/A')}, {data.get('distance', 'N/A')}"
        except Exception as e:
            return f"Error getting commute: {str(e)}"
    
    def _run(self, origin: str, destination: str, mode: str = "driving") -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(origin, destination, mode))


class MorningBriefingTool(BaseTool):
    """Tool to get a complete morning briefing."""
    
    name: str = "get_morning_briefing"
    description: str = "Get a complete morning briefing with weather, calendar, todos, and commute. Use when users ask about their day, morning routine, or want a summary."
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self) -> str:
        """Get complete morning briefing."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            client = self._get_mcp_client()
            data = await client.get_all_morning_data(today)
            
            # Format the briefing
            weather = data.get('weather', {})
            calendar = data.get('calendar', {})
            todos = data.get('todos', {})
            commute = data.get('commute', {})
            
            briefing_parts = [
                f"🌤️ Weather: {weather.get('summary', 'N/A')} - {weather.get('temp_hi', 'N/A')}°F",
                f"📅 Calendar: {calendar.get('total_events', 0)} events today",
                f"✅ Todos: {todos.get('pending_count', 0)} pending tasks",
                f"🚗 Commute: {commute.get('duration', 'N/A')} to {commute.get('destination', 'office')}"
            ]
            
            return "Morning Briefing:\\n" + "\\n".join(briefing_parts)
        except Exception as e:
            return f"Error getting morning briefing: {str(e)}"
    
    def _run(self) -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun())


def get_all_tools():
    """Get all available tools for the agent."""
    return [
        WeatherTool(),
        CalendarTool(),
        TodoTool(),
        CommuteTool(),
        MorningBriefingTool()
    ]
