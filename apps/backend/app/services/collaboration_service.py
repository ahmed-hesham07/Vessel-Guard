"""
Real-time collaboration service for multi-user editing.

This service provides real-time collaboration capabilities including
live editing, user presence, comments, and collaborative features.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.project import Project
from app.db.models.calculation import Calculation
from app.core.config import settings


class CollaborationEventType(str, Enum):
    """Types of collaboration events."""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    DOCUMENT_EDIT = "document_edit"
    COMMENT_ADDED = "comment_added"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    CURSOR_MOVE = "cursor_move"
    SELECTION_CHANGE = "selection_change"
    CALCULATION_UPDATE = "calculation_update"
    PRESENCE_UPDATE = "presence_update"


@dataclass
class CollaborationEvent:
    """Collaboration event data structure."""
    event_type: CollaborationEventType
    user_id: int
    session_id: str
    timestamp: datetime
    data: Dict[str, Any]
    target_id: Optional[str] = None  # Document, calculation, or project ID


class CollaborationService:
    """Service for real-time collaboration features."""
    
    def __init__(self):
        # Active sessions and users
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[int, Set[str]] = {}
        self.document_sessions: Dict[str, Set[str]] = {}
        
        # Collaboration rooms
        self.collaboration_rooms: Dict[str, Dict[str, Any]] = {}
        
        # Event history for new users joining
        self.event_history: Dict[str, List[CollaborationEvent]] = {}
    
    async def join_session(
        self,
        user_id: int,
        session_id: str,
        target_type: str,
        target_id: str,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Join a collaboration session."""
        # Create or get collaboration room
        room_key = f"{target_type}:{target_id}"
        
        if room_key not in self.collaboration_rooms:
            self.collaboration_rooms[room_key] = {
                "active_users": {},
                "document_state": {},
                "comments": [],
                "created_at": datetime.now()
            }
        
        # Add user to session
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "target_type": target_type,
            "target_id": target_id,
            "room_key": room_key,
            "user_data": user_data,
            "joined_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        # Track document sessions
        if room_key not in self.document_sessions:
            self.document_sessions[room_key] = set()
        self.document_sessions[room_key].add(session_id)
        
        # Add user to room
        self.collaboration_rooms[room_key]["active_users"][session_id] = {
            "user_id": user_id,
            "user_data": user_data,
            "joined_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        # Create join event
        event = CollaborationEvent(
            event_type=CollaborationEventType.USER_JOINED,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            data={
                "user_data": user_data,
                "room_key": room_key,
                "active_users": len(self.collaboration_rooms[room_key]["active_users"])
            },
            target_id=target_id
        )
        
        # Store event in history
        if room_key not in self.event_history:
            self.event_history[room_key] = []
        self.event_history[room_key].append(event)
        
        # Limit history size
        if len(self.event_history[room_key]) > 100:
            self.event_history[room_key] = self.event_history[room_key][-50:]
        
        return {
            "session_id": session_id,
            "room_key": room_key,
            "active_users": len(self.collaboration_rooms[room_key]["active_users"]),
            "recent_events": self._get_recent_events(room_key)
        }
    
    async def leave_session(self, session_id: str) -> Dict[str, Any]:
        """Leave a collaboration session."""
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session_data = self.active_sessions[session_id]
        user_id = session_data["user_id"]
        room_key = session_data["room_key"]
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Remove from user sessions
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
        
        # Remove from document sessions
        if room_key in self.document_sessions:
            self.document_sessions[room_key].discard(session_id)
            if not self.document_sessions[room_key]:
                del self.document_sessions[room_key]
        
        # Remove from room
        if room_key in self.collaboration_rooms:
            if session_id in self.collaboration_rooms[room_key]["active_users"]:
                del self.collaboration_rooms[room_key]["active_users"][session_id]
        
        # Create leave event
        event = CollaborationEvent(
            event_type=CollaborationEventType.USER_LEFT,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            data={
                "room_key": room_key,
                "active_users": len(self.collaboration_rooms.get(room_key, {}).get("active_users", {}))
            },
            target_id=session_data["target_id"]
        )
        
        # Store event
        if room_key in self.event_history:
            self.event_history[room_key].append(event)
        
        return {
            "status": "success",
            "session_id": session_id,
            "active_users": len(self.collaboration_rooms.get(room_key, {}).get("active_users", {}))
        }
    
    async def handle_document_edit(
        self,
        session_id: str,
        edit_data: Dict[str, Any]
    ) -> CollaborationEvent:
        """Handle document edit event."""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session_data = self.active_sessions[session_id]
        room_key = session_data["room_key"]
        
        # Update last activity
        self.active_sessions[session_id]["last_activity"] = datetime.now()
        if room_key in self.collaboration_rooms:
            if session_id in self.collaboration_rooms[room_key]["active_users"]:
                self.collaboration_rooms[room_key]["active_users"][session_id]["last_activity"] = datetime.now()
        
        # Create edit event
        event = CollaborationEvent(
            event_type=CollaborationEventType.DOCUMENT_EDIT,
            user_id=session_data["user_id"],
            session_id=session_id,
            timestamp=datetime.now(),
            data=edit_data,
            target_id=session_data["target_id"]
        )
        
        # Store event
        if room_key in self.event_history:
            self.event_history[room_key].append(event)
        
        return event
    
    async def add_comment(
        self,
        session_id: str,
        comment_data: Dict[str, Any]
    ) -> CollaborationEvent:
        """Add a comment to the collaboration."""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session_data = self.active_sessions[session_id]
        room_key = session_data["room_key"]
        
        # Create comment event
        event = CollaborationEvent(
            event_type=CollaborationEventType.COMMENT_ADDED,
            user_id=session_data["user_id"],
            session_id=session_id,
            timestamp=datetime.now(),
            data=comment_data,
            target_id=session_data["target_id"]
        )
        
        # Store comment in room
        if room_key in self.collaboration_rooms:
            comment = {
                "id": comment_data.get("comment_id"),
                "user_id": session_data["user_id"],
                "user_data": session_data["user_data"],
                "content": comment_data.get("content"),
                "position": comment_data.get("position"),
                "timestamp": datetime.now(),
                "session_id": session_id
            }
            self.collaboration_rooms[room_key]["comments"].append(comment)
        
        # Store event
        if room_key in self.event_history:
            self.event_history[room_key].append(event)
        
        return event
    
    async def update_comment(
        self,
        session_id: str,
        comment_id: str,
        update_data: Dict[str, Any]
    ) -> CollaborationEvent:
        """Update a comment."""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session_data = self.active_sessions[session_id]
        room_key = session_data["room_key"]
        
        # Update comment in room
        if room_key in self.collaboration_rooms:
            for comment in self.collaboration_rooms[room_key]["comments"]:
                if comment["id"] == comment_id:
                    comment.update(update_data)
                    comment["updated_at"] = datetime.now()
                    break
        
        # Create update event
        event = CollaborationEvent(
            event_type=CollaborationEventType.COMMENT_UPDATED,
            user_id=session_data["user_id"],
            session_id=session_id,
            timestamp=datetime.now(),
            data={"comment_id": comment_id, **update_data},
            target_id=session_data["target_id"]
        )
        
        # Store event
        if room_key in self.event_history:
            self.event_history[room_key].append(event)
        
        return event
    
    async def handle_cursor_move(
        self,
        session_id: str,
        cursor_data: Dict[str, Any]
    ) -> CollaborationEvent:
        """Handle cursor movement event."""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session_data = self.active_sessions[session_id]
        
        # Create cursor event
        event = CollaborationEvent(
            event_type=CollaborationEventType.CURSOR_MOVE,
            user_id=session_data["user_id"],
            session_id=session_id,
            timestamp=datetime.now(),
            data=cursor_data,
            target_id=session_data["target_id"]
        )
        
        return event
    
    async def handle_calculation_update(
        self,
        session_id: str,
        calculation_data: Dict[str, Any]
    ) -> CollaborationEvent:
        """Handle calculation update event."""
        if session_id not in self.active_sessions:
            raise ValueError("Invalid session")
        
        session_data = self.active_sessions[session_id]
        room_key = session_data["room_key"]
        
        # Create calculation update event
        event = CollaborationEvent(
            event_type=CollaborationEventType.CALCULATION_UPDATE,
            user_id=session_data["user_id"],
            session_id=session_id,
            timestamp=datetime.now(),
            data=calculation_data,
            target_id=session_data["target_id"]
        )
        
        # Store event
        if room_key in self.event_history:
            self.event_history[room_key].append(event)
        
        return event
    
    def get_active_users(self, room_key: str) -> List[Dict[str, Any]]:
        """Get active users in a room."""
        if room_key not in self.collaboration_rooms:
            return []
        
        users = []
        for session_id, user_data in self.collaboration_rooms[room_key]["active_users"].items():
            users.append({
                "session_id": session_id,
                "user_id": user_data["user_id"],
                "user_data": user_data["user_data"],
                "joined_at": user_data["joined_at"],
                "last_activity": user_data["last_activity"]
            })
        
        return users
    
    def get_room_comments(self, room_key: str) -> List[Dict[str, Any]]:
        """Get comments for a room."""
        if room_key not in self.collaboration_rooms:
            return []
        
        return self.collaboration_rooms[room_key]["comments"]
    
    def _get_recent_events(self, room_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events for a room."""
        if room_key not in self.event_history:
            return []
        
        recent_events = self.event_history[room_key][-limit:]
        return [
            {
                "event_type": event.event_type,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "timestamp": event.timestamp,
                "data": event.data,
                "target_id": event.target_id
            }
            for event in recent_events
        ]
    
    def get_user_presence(self, user_id: int) -> Dict[str, Any]:
        """Get user presence information."""
        active_sessions = self.user_sessions.get(user_id, set())
        
        presence_data = {
            "user_id": user_id,
            "active_sessions": len(active_sessions),
            "current_rooms": []
        }
        
        for session_id in active_sessions:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                presence_data["current_rooms"].append({
                    "room_key": session_data["room_key"],
                    "target_type": session_data["target_type"],
                    "target_id": session_data["target_id"],
                    "joined_at": session_data["joined_at"],
                    "last_activity": session_data["last_activity"]
                })
        
        return presence_data
    
    def cleanup_inactive_sessions(self, max_inactive_minutes: int = 30) -> int:
        """Clean up inactive sessions."""
        now = datetime.now()
        sessions_to_remove = []
        
        for session_id, session_data in self.active_sessions.items():
            inactive_time = (now - session_data["last_activity"]).total_seconds() / 60
            if inactive_time > max_inactive_minutes:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            asyncio.create_task(self.leave_session(session_id))
        
        return len(sessions_to_remove) 