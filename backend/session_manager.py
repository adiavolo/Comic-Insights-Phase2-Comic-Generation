import uuid
import json
import os
from datetime import datetime
import logging
from core.logging_config import track_status
from typing import Dict, List, Any, Optional

class SessionManager:
    def __init__(self):
        self.logger = logging.getLogger('comic_insights.debug')
        self.status_logger = logging.getLogger('comic_insights.status')
        self.error_logger = logging.getLogger('comic_insights.error')
        
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.logger.debug("Initializing SessionManager")
        self.ensure_export_dir()
    
    def ensure_export_dir(self):
        """Ensure the export directory exists"""
        export_dir = os.path.join(self.project_root, 'export')
        if not os.path.exists(export_dir):
            self.logger.debug(f"Creating export directory: {export_dir}")
            os.makedirs(export_dir)
    
    @track_status("SessionManagement")
    def create_session(self) -> str:
        """Create a new session and return its ID"""
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        self.sessions[session_id] = {
            "created_at": created_at,
            "history": [],
            "status": "active"
        }
        
        self.logger.info(f"Created new session: {session_id}")
        return session_id
    
    @track_status("SessionManagement")
    def add_entry(self, session_id: str, prompt: str, style: str, image: str, plot: str) -> Dict[str, Any]:
        """Add a new generation entry to the session history"""
        if session_id not in self.sessions:
            error_msg = f"Session {session_id} not found"
            self.error_logger.error(error_msg)
            raise ValueError(error_msg)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "style": style,
            "image": image,
            "plot": plot
        }
        
        self.logger.debug(f"Adding entry to session {session_id}: {json.dumps(entry, indent=2)}")
        self.sessions[session_id]["history"].append(entry)
        
        # Log status update
        self.status_logger.info(
            f"Added entry to session {session_id}",
            extra={
                'status_data': {
                    'session_id': session_id,
                    'entry_count': len(self.sessions[session_id]["history"]),
                    'latest_entry': entry['timestamp']
                }
            }
        )
        
        return entry
    
    @track_status("SessionManagement")
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the generation history for a session"""
        if session_id not in self.sessions:
            error_msg = f"Session {session_id} not found"
            self.error_logger.error(error_msg)
            raise ValueError(error_msg)
        
        history = self.sessions[session_id]["history"]
        self.logger.debug(f"Retrieved history for session {session_id}: {len(history)} entries")
        return history
    
    @track_status("SessionManagement")
    def export_session(self, session_id: str) -> str:
        """Export session data to a JSON file"""
        if session_id not in self.sessions:
            error_msg = f"Session {session_id} not found"
            self.error_logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            export_path = os.path.join(self.project_root, 'export', f'session_{session_id}.json')
            
            # Add export metadata
            export_data = {
                "session_id": session_id,
                "exported_at": datetime.now().isoformat(),
                "data": self.sessions[session_id]
            }
            
            self.logger.info(f"Exporting session {session_id} to {export_path}")
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.status_logger.info(
                f"Session exported successfully",
                extra={
                    'status_data': {
                        'session_id': session_id,
                        'export_path': export_path,
                        'entry_count': len(self.sessions[session_id]["history"])
                    }
                }
            )
            
            return export_path
            
        except Exception as e:
            self.error_logger.exception(
                f"Failed to export session {session_id}",
                extra={
                    'session_id': session_id,
                    'error': str(e)
                }
            )
            raise
    
    @track_status("SessionManagement")
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status information about a session"""
        if session_id not in self.sessions:
            error_msg = f"Session {session_id} not found"
            self.error_logger.error(error_msg)
            raise ValueError(error_msg)
        
        session = self.sessions[session_id]
        status_info = {
            "session_id": session_id,
            "created_at": session["created_at"],
            "status": session["status"],
            "entry_count": len(session["history"]),
            "last_updated": session["history"][-1]["timestamp"] if session["history"] else session["created_at"]
        }
        
        self.logger.debug(f"Session status: {json.dumps(status_info, indent=2)}")
        return status_info 