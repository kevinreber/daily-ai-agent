"""Flask API for the AI agent - provides web endpoints for all agent functionality."""

import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import BadRequest, InternalServerError
from loguru import logger
from typing import Dict, Any, Optional

from .agent.orchestrator import AgentOrchestrator
from .services.mcp_client import MCPClient
from .models.config import get_settings


def create_app(testing: bool = False) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    settings = get_settings()
    
    # Configure CORS
    CORS(app, origins=settings.allowed_origins)
    
    # Configure rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute} per minute"]
    )
    
    # Initialize services
    orchestrator = AgentOrchestrator()
    mcp_client = MCPClient()
    
    @app.errorhandler(Exception)
    def handle_error(error):
        """Global error handler."""
        logger.error(f"API error: {error}")
        
        if isinstance(error, BadRequest):
            return jsonify({"error": "Invalid request format"}), 400
        elif isinstance(error, Exception):
            return jsonify({"error": str(error)}), 500
        
        return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "Daily AI Agent API",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
            "mcp_server": settings.mcp_server_url,
            "ai_enabled": orchestrator.is_conversational()
        })
    
    @app.route('/chat', methods=['POST'])
    @limiter.limit("10 per minute")
    async def chat():
        """
        Natural language conversation endpoint.
        
        Body: {"message": "What's my day looking like?"}
        """
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                raise BadRequest("Missing 'message' field in request body")
            
            message = data['message'].strip()
            if not message:
                raise BadRequest("Message cannot be empty")
            
            if not orchestrator.is_conversational():
                return jsonify({
                    "error": "Conversational AI not available",
                    "message": "OpenAI API key required for chat functionality"
                }), 503
            
            logger.info(f"Chat request: {message}")
            response = await orchestrator.chat(message)
            
            return jsonify({
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
        except BadRequest as e:
            raise e
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/briefing', methods=['GET'])
    @limiter.limit("20 per minute")
    async def briefing():
        """
        Get AI-powered morning briefing.
        
        Query params:
        - type: 'basic' (default) or 'smart' (AI-powered)
        """
        try:
            briefing_type = request.args.get('type', 'basic').lower()
            
            if briefing_type == 'smart':
                if not orchestrator.is_conversational():
                    return jsonify({
                        "error": "Smart briefing not available",
                        "message": "OpenAI API key required for AI briefings"
                    }), 503
                
                logger.info("Generating smart briefing")
                briefing_text = await orchestrator.get_smart_briefing()
                
                return jsonify({
                    "type": "smart",
                    "briefing": briefing_text,
                    "timestamp": datetime.now().isoformat()
                })
            
            else:  # Basic briefing
                logger.info("Generating basic briefing")
                today = datetime.now().strftime('%Y-%m-%d')
                data = await mcp_client.get_all_morning_data(today)
                
                return jsonify({
                    "type": "basic",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Briefing error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/tools/weather', methods=['GET'])
    async def get_weather():
        """
        Get weather forecast.
        
        Query params:
        - location: Location name (default: user's location)
        - when: 'today' or 'tomorrow' (default: 'today')
        """
        try:
            location = request.args.get('location', settings.user_location)
            when = request.args.get('when', 'today')
            
            logger.info(f"Weather request: {location}, {when}")
            weather_data = await mcp_client.get_weather(location, when)
            
            return jsonify({
                "tool": "weather",
                "data": weather_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/tools/todos', methods=['GET'])
    async def get_todos():
        """
        Get todo items.
        
        Query params:
        - bucket: 'work', 'home', 'errands', 'personal' (default: 'work')
        - include_completed: true/false (default: false)
        """
        try:
            bucket = request.args.get('bucket', 'work')
            include_completed = request.args.get('include_completed', 'false').lower() == 'true'
            
            logger.info(f"Todos request: {bucket}, include_completed={include_completed}")
            todos_data = await mcp_client.get_todos(bucket, include_completed)
            
            return jsonify({
                "tool": "todos",
                "data": todos_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Todos error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/tools/calendar', methods=['GET'])
    async def get_calendar():
        """
        Get calendar events.
        
        Query params:
        - date: YYYY-MM-DD format (default: today)
        """
        try:
            date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            logger.info(f"Calendar request: {date}")
            calendar_data = await mcp_client.get_calendar_events(date)
            
            return jsonify({
                "tool": "calendar", 
                "data": calendar_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Calendar error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/tools/commute', methods=['GET'])
    async def get_commute():
        """
        Get commute information.
        
        Query params:
        - origin: Starting location (default: user's default)
        - destination: Destination (default: user's default)  
        - mode: 'driving', 'transit', 'bicycling', 'walking' (default: 'driving')
        """
        try:
            origin = request.args.get('origin', settings.default_commute_origin)
            destination = request.args.get('destination', settings.default_commute_destination)
            mode = request.args.get('mode', 'driving')
            
            logger.info(f"Commute request: {origin} -> {destination} ({mode})")
            commute_data = await mcp_client.get_commute(origin, destination, mode)
            
            return jsonify({
                "tool": "commute",
                "data": commute_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Commute error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/tools', methods=['GET'])
    def list_tools():
        """List all available tools and their endpoints."""
        return jsonify({
            "tools": {
                "weather": {
                    "endpoint": "/tools/weather",
                    "method": "GET",
                    "description": "Get weather forecast",
                    "params": ["location", "when"]
                },
                "todos": {
                    "endpoint": "/tools/todos", 
                    "method": "GET",
                    "description": "Get todo items",
                    "params": ["bucket", "include_completed"]
                },
                "calendar": {
                    "endpoint": "/tools/calendar",
                    "method": "GET", 
                    "description": "Get calendar events",
                    "params": ["date"]
                },
                "commute": {
                    "endpoint": "/tools/commute",
                    "method": "GET",
                    "description": "Get commute information", 
                    "params": ["origin", "destination", "mode"]
                }
            },
            "ai_features": {
                "chat": {
                    "endpoint": "/chat",
                    "method": "POST",
                    "description": "Natural language conversation",
                    "body": {"message": "string"}
                },
                "briefing": {
                    "endpoint": "/briefing",
                    "method": "GET",
                    "description": "Morning briefing (basic or smart)",
                    "params": ["type"]
                }
            },
            "available": orchestrator.is_conversational(),
            "timestamp": datetime.now().isoformat()
        })
    
    return app
