"""Conversation memory service for maintaining chat history and context."""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from loguru import logger

from ..models.config import get_settings


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Conversation:
    """Represents a conversation with metadata and message history."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = None

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a new message to the conversation."""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.messages.append(message)
        self.last_activity = datetime.now()

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get the most recent messages, limited by count."""
        return self.messages[-limit:] if limit > 0 else self.messages

    def get_messages_since(self, since: datetime) -> List[Message]:
        """Get messages since a specific timestamp."""
        return [msg for msg in self.messages if msg.timestamp > since]

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        data['messages'] = [Message.from_dict(msg) for msg in data['messages']]
        return cls(**data)


class ConversationMemoryService:
    """Service for managing conversation memory and history."""

    def __init__(self):
        self.settings = get_settings()
        # In-memory storage for conversations (could be replaced with Redis/DB)
        self._conversations: Dict[str, Conversation] = {}
        # Maximum number of conversations to keep in memory
        self._max_conversations = 100
        # Maximum age for conversations (in hours)
        self._max_age_hours = 24
        
        logger.info("ConversationMemoryService initialized")

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            metadata: Optional metadata for the session
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        conversation = Conversation(
            session_id=session_id,
            created_at=now,
            last_activity=now,
            messages=[],
            metadata=metadata or {}
        )
        
        self._conversations[session_id] = conversation
        self._cleanup_old_conversations()
        
        logger.info(f"Created new conversation session: {session_id}")
        return session_id

    def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """
        Get a conversation by session ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Conversation object or None if not found
        """
        conversation = self._conversations.get(session_id)
        
        if conversation:
            # Check if conversation is too old
            if self._is_conversation_expired(conversation):
                self.delete_session(session_id)
                return None
                
        return conversation

    def add_message(self, session_id: str, role: str, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            session_id: The session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            True if message was added successfully
        """
        if not self.settings.enable_memory:
            logger.debug("Memory disabled, not storing message")
            return False

        conversation = self.get_conversation(session_id)
        if not conversation:
            logger.warning(f"Session {session_id} not found, cannot add message")
            return False

        conversation.add_message(role, content, metadata)
        logger.debug(f"Added {role} message to session {session_id}")
        return True

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Message]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: The session identifier
            limit: Maximum number of recent messages to return
            
        Returns:
            List of recent messages
        """
        if not self.settings.enable_memory:
            return []

        conversation = self.get_conversation(session_id)
        if not conversation:
            return []

        return conversation.get_recent_messages(limit)

    def get_conversation_context(self, session_id: str, limit: int = 10) -> str:
        """
        Get formatted conversation context for AI prompts.
        
        Args:
            session_id: The session identifier
            limit: Maximum number of recent messages to include
            
        Returns:
            Formatted conversation history as a string
        """
        if not self.settings.enable_memory:
            return ""

        messages = self.get_conversation_history(session_id, limit)
        if not messages:
            return ""

        context_lines = []
        for i, msg in enumerate(messages):
            role_prefix = "User" if msg.role == "user" else "Assistant"
            # Add more structure to help LLM understand context better
            context_lines.append(f"[{i+1}] {role_prefix}: {msg.content}")

        formatted_context = "\n".join(context_lines)
        
        # Find the last assistant message to check for questions/offers
        last_assistant_msg = None
        for msg in reversed(messages):
            if msg.role == "assistant":
                last_assistant_msg = msg
                break
        
        # Analyze conversation flow and context patterns
        flow_guidance = ""
        
        # Look at recent messages for conversation flow analysis
        recent_messages = messages[-6:] if len(messages) > 6 else messages  # Last 6 messages max
        
        # Check if the last assistant message contains an offer or question
        if last_assistant_msg:
            last_msg_lower = last_assistant_msg.content.lower()
            
            # Check for offers/questions
            if any(phrase in last_msg_lower for phrase in [
                "would you like", "do you want", "let me know", "just ask", "feel free", 
                "please let me know", "i can provide", "can provide more details", "can provide more"
            ]):
                flow_guidance = f"""

CONVERSATIONAL FLOW: The user's last response may be answering a question or responding to an offer 
I made in my previous message: "{last_assistant_msg.content[:150]}..." 
Consider if their response like "yes", "please", "sure", "no thanks", "provide all", "show me" relates to this context."""

        # Analyze recent conversation themes by looking at user questions and topics
        conversation_themes = self._analyze_conversation_themes(recent_messages)
        
        if conversation_themes:
            theme_guidance = "\n\nCONVERSATION THEMES: Based on recent discussion, the user has been asking about:\n"
            for theme, confidence in conversation_themes.items():
                theme_guidance += f"- {theme} (confidence: {confidence})\n"
            theme_guidance += "If the user asks for 'all of them', 'details', 'more info', consider what topic they were most recently discussing."
            flow_guidance += theme_guidance
        
        return f"""
CONVERSATION HISTORY (most relevant for understanding context):
{formatted_context}

IMPORTANT CONTEXT RULES:
1. When the user asks about "this", "that", "it", or uses pronouns, they refer to specific items mentioned above
2. When the user gives short responses like "yes", "please", "sure", "no", they are likely responding to my last question or offer
3. Use this history to understand conversational flow and provide contextual responses, not generic information{flow_guidance}"""
    
    def _analyze_conversation_themes(self, recent_messages: List[Message]) -> Dict[str, str]:
        """
        Analyze recent conversation patterns to identify dominant themes.
        Uses multiple signals: user questions, tool mentions, and response patterns.
        """
        themes = {}
        
        # Analyze user questions and requests for more robust theme detection
        user_questions = [msg.content for msg in recent_messages if msg.role == "user"]
        assistant_responses = [msg.content for msg in recent_messages if msg.role == "assistant"]
        
        # Look for patterns in user questions (more reliable than keyword matching)
        for question in user_questions[-3:]:  # Last 3 user questions
            q_lower = question.lower()
            
            # Financial questions - broader patterns
            if any(phrase in q_lower for phrase in [
                'what stock', 'stock instruments', 'tracking', 'financial', 'market',
                'crypto', 'price', 'portfolio', 'investment'
            ]):
                themes['Financial/Market Data'] = 'high'
            
            # Calendar questions
            if any(phrase in q_lower for phrase in [
                'events', 'calendar', 'schedule', 'meeting', 'appointment', 'today'
            ]):
                themes['Calendar/Schedule'] = 'high'
                
            # Task questions  
            if any(phrase in q_lower for phrase in [
                'tasks', 'todo', 'pending', 'work', 'errands', 'personal'
            ]):
                themes['Tasks/Todos'] = 'high'
                
        # Look for tool mentions in assistant responses (most reliable signal)
        for response in assistant_responses[-2:]:  # Last 2 assistant responses
            r_lower = response.lower()
            
            # Check for mentions of specific data types (more reliable than keywords)
            if 'instruments tracked' in r_lower or '7 instruments' in r_lower:
                themes['Financial/Market Data'] = 'high'
            elif 'event scheduled' in r_lower or 'calendar' in r_lower:
                themes['Calendar/Schedule'] = 'medium'  
            elif 'pending tasks' in r_lower or 'todo' in r_lower:
                themes['Tasks/Todos'] = 'medium'
                
        return themes

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was deleted
        """
        if session_id in self._conversations:
            del self._conversations[session_id]
            logger.info(f"Deleted conversation session: {session_id}")
            return True
        return False

    def list_sessions(self, active_only: bool = True) -> List[str]:
        """
        List all conversation session IDs.
        
        Args:
            active_only: If True, only return non-expired sessions
            
        Returns:
            List of session IDs
        """
        if active_only:
            self._cleanup_old_conversations()
        
        return list(self._conversations.keys())

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata and statistics.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Session information dictionary
        """
        conversation = self.get_conversation(session_id)
        if not conversation:
            return None

        return {
            'session_id': session_id,
            'created_at': conversation.created_at.isoformat(),
            'last_activity': conversation.last_activity.isoformat(),
            'message_count': len(conversation.messages),
            'metadata': conversation.metadata
        }

    def _cleanup_old_conversations(self):
        """Remove expired conversations from memory."""
        cutoff_time = datetime.now() - timedelta(hours=self._max_age_hours)
        expired_sessions = []
        
        for session_id, conversation in self._conversations.items():
            if conversation.last_activity < cutoff_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._conversations[session_id]
            logger.debug(f"Cleaned up expired session: {session_id}")

        # Also limit total number of conversations
        if len(self._conversations) > self._max_conversations:
            # Sort by last activity and remove oldest
            sorted_sessions = sorted(
                self._conversations.items(),
                key=lambda x: x[1].last_activity
            )
            
            excess_count = len(self._conversations) - self._max_conversations
            for session_id, _ in sorted_sessions[:excess_count]:
                del self._conversations[session_id]
                logger.debug(f"Cleaned up old session due to limit: {session_id}")

    def _is_conversation_expired(self, conversation: Conversation) -> bool:
        """Check if a conversation has expired."""
        cutoff_time = datetime.now() - timedelta(hours=self._max_age_hours)
        return conversation.last_activity < cutoff_time

    def get_stats(self) -> Dict[str, Any]:
        """Get memory service statistics."""
        total_messages = sum(len(conv.messages) for conv in self._conversations.values())
        
        return {
            'total_sessions': len(self._conversations),
            'total_messages': total_messages,
            'memory_enabled': self.settings.enable_memory,
            'max_conversations': self._max_conversations,
            'max_age_hours': self._max_age_hours
        }


# Global memory service instance
_memory_service = None


def get_memory_service() -> ConversationMemoryService:
    """Get the global memory service instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = ConversationMemoryService()
    return _memory_service
