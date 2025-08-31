"""HTTP client for communicating with the deployed MCP server."""

import httpx
import asyncio
from typing import Dict, Any, Optional
from loguru import logger

from ..models.config import get_settings


class MCPClient:
    """HTTP client for calling MCP server tools."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.mcp_server_url.rstrip('/')
        self.timeout = self.settings.mcp_server_timeout
    
    async def call_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool on the MCP server.
        
        Args:
            tool_name: Name of the tool (e.g., 'weather.get_daily')
            input_data: Input parameters for the tool
            
        Returns:
            Tool response data
            
        Raises:
            Exception: If the tool call fails
        """
        url = f"{self.base_url}/tools/{tool_name}"
        
        logger.info(f"Calling MCP tool: {tool_name} with data: {input_data}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=input_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()
                
                logger.success(f"Tool {tool_name} completed successfully")
                return result
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} calling {tool_name}: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.TimeoutException:
            error_msg = f"Timeout calling {tool_name} after {self.timeout}s"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error calling {tool_name}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def get_weather(self, location: str, when: str = "today") -> Dict[str, Any]:
        """Get weather forecast for a location."""
        return await self.call_tool("weather.get_daily", {
            "location": location,
            "when": when
        })
    
    async def get_calendar_events(self, date: str) -> Dict[str, Any]:
        """Get calendar events for a specific date."""
        return await self.call_tool("calendar.list_events", {
            "date": date
        })
    
    async def get_calendar_events_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get calendar events for a date range (more efficient than multiple single-date calls)."""
        return await self.call_tool("calendar.list_events_range", {
            "start_date": start_date,
            "end_date": end_date
        })
    
    async def get_todos(self, bucket: Optional[str] = None, include_completed: bool = False) -> Dict[str, Any]:
        """Get todo items from a bucket or all buckets if bucket is None."""
        params = {"include_completed": include_completed}
        if bucket is not None:
            params["bucket"] = bucket
        return await self.call_tool("todo.list", params)
    
    async def get_commute(self, origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
        """Get basic commute information between locations."""
        return await self.call_tool("mobility.get_commute", {
            "origin": origin,
            "destination": destination,
            "mode": mode
        })
    
    async def get_commute_options(self, direction: str, departure_time: str = None, 
                                include_driving: bool = True, include_transit: bool = True) -> Dict[str, Any]:
        """Get comprehensive commute options with driving and transit (Caltrain + shuttle)."""
        params = {
            "direction": direction,
            "include_driving": include_driving,
            "include_transit": include_transit
        }
        if departure_time:
            params["departure_time"] = departure_time
        return await self.call_tool("mobility.get_commute_options", params)
    
    async def get_shuttle_schedule(self, origin: str, destination: str, departure_time: str = None) -> Dict[str, Any]:
        """Get MV Connector shuttle schedule between stops."""
        params = {
            "origin": origin,
            "destination": destination
        }
        if departure_time:
            params["departure_time"] = departure_time
        return await self.call_tool("mobility.get_shuttle_schedule", params)
    
    async def get_all_morning_data(self, date: str) -> Dict[str, Any]:
        """
        Get all morning routine data in parallel for speed.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Combined data from all tools
        """
        settings = get_settings()
        
        # Call all tools in parallel for speed
        tasks = [
            self.get_weather(settings.user_location),
            self.get_calendar_events(date),
            self.get_todos("work"),  # Still use "work" for morning briefing
            self.get_commute_options("to_work")  # Use enhanced commute options for morning briefing
        ]
        
        try:
            weather, calendar, todos, commute = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions gracefully
            result = {}
            
            if isinstance(weather, Exception):
                logger.warning(f"Weather call failed: {weather}")
                result["weather"] = {"error": str(weather)}
            else:
                result["weather"] = weather
                
            if isinstance(calendar, Exception):
                logger.warning(f"Calendar call failed: {calendar}")
                result["calendar"] = {"error": str(calendar)}
            else:
                result["calendar"] = calendar
                
            if isinstance(todos, Exception):
                logger.warning(f"Todos call failed: {todos}")
                result["todos"] = {"error": str(todos)}
            else:
                result["todos"] = todos
                
            if isinstance(commute, Exception):
                logger.warning(f"Commute call failed: {commute}")
                result["commute"] = {"error": str(commute)}
            else:
                result["commute"] = commute
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting morning data: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            url = f"{self.base_url}/health"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"MCP server health check failed: {e}")
            return False
