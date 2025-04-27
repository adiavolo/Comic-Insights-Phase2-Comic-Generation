import uuid
import json
from datetime import datetime
import os

class SessionManager:
    def __init__(self):
        self.sessions = {}
        # Get the absolute path to the project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ensure_export_dir()

    def ensure_export_dir(self):
        """Ensure the export directory exists"""
        export_dir = os.path.join(self.project_root, 'export')
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def create_session(self):
        """Create a new session and return its ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "history": []
        }
        return session_id

    def add_entry(self, session_id, prompt, style, image, plot):
        """Add a new generation entry to the session history"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "style": style,
            "image": image,  # This will be the image path after saving
            "plot": plot
        }
        self.sessions[session_id]["history"].append(entry)
        return entry

    def get_history(self, session_id):
        """Get the generation history for a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]["history"]

    def export_session(self, session_id):
        """Export session data to a JSON file"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        export_path = os.path.join(self.project_root, 'export', f'session_{session_id}.json')
        with open(export_path, 'w') as f:
            json.dump(self.sessions[session_id], f, indent=2)
        return export_path 