"""Flask API for the AI agent - provides web endpoints for all agent functionality."""

import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger, swag_from
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
    
    # Configure Swagger UI
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Daily AI Agent API",
            "description": "Intelligent morning routine assistant with conversational AI",
            "contact": {
                "responsibleOrganization": "Personal Learning Project",
                "responsibleDeveloper": "Kevin Reber",
            },
            "version": "0.1.0"
        },
        "host": "localhost:8001" if settings.environment == "development" else None,
        "basePath": "/",
        "schemes": ["http"] if settings.environment == "development" else ["https"],
        "produces": ["application/json"],
        "consumes": ["application/json"]
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
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
        """Health check endpoint.
        ---
        tags:
          - System
        responses:
          200:
            description: Service health status
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
                service:
                  type: string
                  example: "Daily AI Agent API"
                version:
                  type: string
                  example: "0.1.0"
                ai_enabled:
                  type: boolean
                  example: true
                mcp_server:
                  type: string
                  example: "https://web-production-66f9.up.railway.app"
        """
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
        """Natural language conversation with AI assistant
        ---
        tags:
          - AI Features
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  example: "What's my day looking like?"
                  description: "Natural language query to the AI assistant"
        responses:
          200:
            description: AI assistant response
            schema:
              type: object
              properties:
                response:
                  type: string
                  example: "Today you should focus on your 3 pending tasks. Weather is nice at 77°F!"
                timestamp:
                  type: string
                  example: "2025-08-11T00:16:05.255826"
          400:
            description: Invalid request format
          503:
            description: AI features not available (missing OpenAI API key)
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
        """Get morning briefing (basic data or AI-powered)
        ---
        tags:
          - AI Features
        parameters:
          - name: type
            in: query
            type: string
            enum: ['basic', 'smart']
            default: 'basic'
            description: "Type of briefing: 'basic' (structured data) or 'smart' (AI-generated)"
        responses:
          200:
            description: Morning briefing
            schema:
              type: object
              properties:
                type:
                  type: string
                  example: "smart"
                briefing:
                  type: string
                  example: "Good morning! Weather is 77°F, you have 3 pending tasks..."
                timestamp:
                  type: string
          503:
            description: Smart briefing not available (missing OpenAI API key)
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
        """Get weather forecast with real OpenWeatherMap data
        ---
        tags:
          - Tools
        parameters:
          - name: location
            in: query
            type: string
            default: "San Francisco"
            description: "Location name (city, state/country)"
            example: "San Francisco"
          - name: when
            in: query
            type: string
            enum: ['today', 'tomorrow']
            default: 'today'
            description: "Time period for forecast"
        responses:
          200:
            description: Weather forecast data
            schema:
              type: object
              properties:
                tool:
                  type: string
                  example: "weather"
                data:
                  type: object
                  properties:
                    location:
                      type: string
                      example: "San Francisco, US"
                    temp_hi:
                      type: number
                      example: 77.4
                    temp_lo:
                      type: number
                      example: 57.1
                    summary:
                      type: string
                      example: "Scattered Clouds"
                timestamp:
                  type: string
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
    
    @app.route('/tools/financial', methods=['POST'])
    async def get_financial():
        """Get real-time stock and cryptocurrency market data
        ---
        tags:
          - Tools
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - symbols
              properties:
                symbols:
                  type: array
                  items:
                    type: string
                  example: ["MSFT", "BTC", "ETH"]
                  description: "List of stock/crypto symbols to fetch"
                data_type:
                  type: string
                  enum: ['stocks', 'crypto', 'mixed']
                  default: 'mixed'
                  description: "Type of financial data to retrieve"
        responses:
          200:
            description: Financial market data
            schema:
              type: object
              properties:
                tool:
                  type: string
                  example: "financial"
                data:
                  type: object
                  properties:
                    summary:
                      type: string
                      example: "📊 3 instruments tracked | 📈 2 gaining | 🏆 Best: BTC (+2.3%)"
                    total_items:
                      type: integer
                      example: 3
                    market_status:
                      type: string
                      example: "mixed"
                    data:
                      type: array
                      items:
                        type: object
                        properties:
                          symbol:
                            type: string
                            example: "MSFT"
                          name:
                            type: string
                            example: "Microsoft Corporation"
                          price:
                            type: number
                            example: 522.04
                          change:
                            type: number
                            example: 1.2
                          change_percent:
                            type: number
                            example: 0.23
                          currency:
                            type: string
                            example: "USD"
                          data_type:
                            type: string
                            example: "stocks"
                timestamp:
                  type: string
          400:
            description: Invalid request format
          500:
            description: Server error
        """
        try:
            data = request.get_json()
            if not data or 'symbols' not in data:
                return jsonify({"error": "Missing 'symbols' field in request body"}), 400
            
            symbols = data['symbols']
            data_type = data.get('data_type', 'mixed')
            
            if not isinstance(symbols, list) or not symbols:
                return jsonify({"error": "'symbols' must be a non-empty array"}), 400
            
            logger.info(f"Financial request: {symbols} ({data_type})")
            financial_data = await mcp_client.call_tool("financial.get_data", {
                "symbols": symbols,
                "data_type": data_type
            })
            
            return jsonify({
                "tool": "financial",
                "data": financial_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Financial error: {e}")
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
                },
                "financial": {
                    "endpoint": "/tools/financial",
                    "method": "POST",
                    "description": "Get real-time stock and crypto prices",
                    "params": ["symbols", "data_type"]
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
