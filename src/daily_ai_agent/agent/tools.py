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


class CalendarRangeInput(BaseModel):
    """Input schema for calendar range tool."""
    start_date: str = Field(description="Start date of the range in YYYY-MM-DD format")
    end_date: str = Field(description="End date of the range in YYYY-MM-DD format")


class CalendarCreateInput(BaseModel):
    """Input schema for calendar create tool."""
    title: str = Field(description="Event title/summary")
    start_time: str = Field(description="Event start time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    end_time: str = Field(description="Event end time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    description: Optional[str] = Field(default=None, description="Event description/notes")
    location: Optional[str] = Field(default=None, description="Event location")
    attendees: Optional[list] = Field(default=None, description="List of attendee email addresses")
    calendar_name: str = Field(default="primary", description="Target calendar name")
    all_day: bool = Field(default=False, description="Whether this is an all-day event")


class TodoInput(BaseModel):
    """Input schema for todo tool.""" 
    bucket: str = Field(default="work", description="Todo bucket: 'work', 'home', 'errands', or 'personal'")


class CommuteInput(BaseModel):
    """Input schema for commute tool."""
    origin: str = Field(description="Starting location")
    destination: str = Field(description="Destination location")
    mode: str = Field(default="driving", description="Transport mode: 'driving', 'transit', 'bicycling', 'walking'")


class FinancialInput(BaseModel):
    """Input schema for financial tool."""
    symbols: list = Field(default=None, description="List of stock/crypto symbols like ['MSFT', 'BTC', 'ETH']. If not provided, shows default tracked portfolio: MSFT, NVDA, BTC, ETH, VOO, SMR, GOOGL")
    data_type: str = Field(default="mixed", description="Type: 'stocks', 'crypto', or 'mixed'")


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


class CalendarRangeTool(BaseTool):
    """Tool to get calendar events for a date range (more efficient than multiple single-date calls)."""
    
    name: str = "get_calendar_range"
    description: str = "Get calendar events for a date range. Use when users ask about their week, multiple days, or date ranges. Much more efficient than multiple single-date calls."
    args_schema: Type[BaseModel] = CalendarRangeInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, start_date: str, end_date: str) -> str:
        """Get calendar events for a date range."""
        try:
            client = self._get_mcp_client()
            data = await client.get_calendar_events_range(start_date, end_date)
            events = data.get('events', [])
            total = data.get('total_events', 0)
            
            if total == 0:
                return f"No events scheduled from {start_date} to {end_date}"
            
            # Group events by date for better readability
            events_by_date = {}
            for event in events:
                event_date = event.get('start_time', '')[:10]  # Extract YYYY-MM-DD
                if event_date not in events_by_date:
                    events_by_date[event_date] = []
                events_by_date[event_date].append(event)
            
            result_lines = [f"{total} events from {start_date} to {end_date}:"]
            for date, day_events in sorted(events_by_date.items()):
                result_lines.append(f"\n{date}:")
                for event in day_events[:3]:  # Show max 3 events per day
                    time_str = event.get('start_time', '')
                    if 'T' in time_str:
                        time_part = time_str.split('T')[1][:5]  # Extract HH:MM
                        result_lines.append(f"  - {event.get('title', 'N/A')} at {time_part}")
                    else:
                        result_lines.append(f"  - {event.get('title', 'N/A')} (all day)")
                
                if len(day_events) > 3:
                    result_lines.append(f"  ... and {len(day_events) - 3} more")
            
            return "\\n".join(result_lines)
        except Exception as e:
            return f"Error getting calendar range: {str(e)}"
    
    def _run(self, start_date: str, end_date: str) -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(start_date, end_date))


class CalendarCreateTool(BaseTool):
    """Tool to create new calendar events."""
    
    name: str = "create_calendar_event"
    description: str = "Create a new calendar event. Use when users want to schedule meetings, appointments, or events. Supports conflict detection and natural language parsing."
    args_schema: Type[BaseModel] = CalendarCreateInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, title: str, start_time: str, end_time: str, 
                   description: Optional[str] = None, location: Optional[str] = None,
                   attendees: Optional[list] = None, calendar_name: str = "primary",
                   all_day: bool = False) -> str:
        """Create a new calendar event."""
        try:
            client = self._get_mcp_client()
            
            # Prepare the data for the MCP server
            event_data = {
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "description": description,
                "location": location,
                "attendees": attendees,
                "calendar_name": calendar_name,
                "all_day": all_day
            }
            
            # Remove None values
            event_data = {k: v for k, v in event_data.items() if v is not None}
            
            result = await client.call_tool("calendar.create_event", event_data)
            
            if result.get('success'):
                message = result.get('message', 'Event created successfully')
                conflicts = result.get('conflicts', [])
                
                if conflicts:
                    conflict_details = []
                    for conflict in conflicts:
                        conflict_details.append(f"- {conflict.get('title', 'Unknown')} at {conflict.get('start_time', 'Unknown time')}")
                    
                    message += f"\\n\\n⚠️ Conflicts detected:\\n" + "\\n".join(conflict_details)
                    message += "\\n\\nYou may want to reschedule one of these events."
                
                # Add event URL if available
                if result.get('event_url'):
                    message += f"\\n\\n📅 View event: {result['event_url']}"
                
                return message
            else:
                return f"❌ Failed to create event: {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ Error creating calendar event: {str(e)}"
    
    def _run(self, title: str, start_time: str, end_time: str, 
             description: Optional[str] = None, location: Optional[str] = None,
             attendees: Optional[list] = None, calendar_name: str = "primary",
             all_day: bool = False) -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(title, start_time, end_time, description, 
                                    location, attendees, calendar_name, all_day))


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


class FinancialTool(BaseTool):
    """Tool to get financial data for stocks and cryptocurrencies."""
    
    name: str = "get_financial_data"
    description: str = "Get financial data for stocks and cryptocurrencies. Use when users ask about: stock prices, crypto prices, portfolio data, tracked symbols, market information, instruments we're tracking, what stocks/crypto we monitor, or any financial/investment questions. Default tracked symbols: MSFT, NVDA, BTC, ETH, VOO, SMR, GOOGL."
    args_schema: Type[BaseModel] = FinancialInput
    
    def _get_mcp_client(self) -> MCPClient:
        """Get MCP client instance."""
        return MCPClient()
    
    async def _arun(self, symbols: list = None, data_type: str = "mixed") -> str:
        """Get financial data."""
        try:
            # Use default symbols if none provided
            if not symbols:
                symbols = ["MSFT", "NVDA", "BTC", "ETH", "VOO", "SMR", "GOOGL"]
            
            client = self._get_mcp_client()
            data = await client.call_tool("financial.get_data", {"symbols": symbols, "data_type": data_type})
            
            if 'data' in data:
                financial_items = data['data']
                summary = data.get('summary', '')
                
                # Format the response
                result_parts = [f"💰 Financial Update: {summary}"]
                
                for item in financial_items:
                    symbol = item['symbol']
                    name = item['name']
                    price = item['price']
                    change = item['change']
                    change_percent = item['change_percent']
                    
                    # Format change with appropriate emoji
                    if change >= 0:
                        change_str = f"📈 +${change:.2f} (+{change_percent:.1f}%)"
                    else:
                        change_str = f"📉 ${change:.2f} ({change_percent:.1f}%)"
                    
                    result_parts.append(f"{symbol} ({name}): ${price:.2f} {change_str}")
                
                return "\\n".join(result_parts)
            else:
                return f"Financial data: {data.get('summary', 'No data available')}"
                
        except Exception as e:
            return f"Error getting financial data: {str(e)}"
    
    def _run(self, symbols: list = None, data_type: str = "mixed") -> str:
        """Sync wrapper for async call."""
        return asyncio.run(self._arun(symbols, data_type))


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
            
            # Get financial data for your tracked symbols
            financial_data = await client.call_tool("financial.get_data", {
                "symbols": ["MSFT", "NVDA", "BTC", "ETH", "VOO", "SMR", "GOOGL"],
                "data_type": "mixed"
            })
            
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
            
            # Add financial summary
            if financial_data and 'summary' in financial_data:
                briefing_parts.append(f"💰 Markets: {financial_data['summary']}")
            
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
        CalendarRangeTool(),
        CalendarCreateTool(),
        TodoTool(),
        CommuteTool(),
        FinancialTool(),
        MorningBriefingTool()
    ]
