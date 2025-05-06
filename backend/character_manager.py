import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import uuid4
from .llm_utils import call_llm, call_llm_json
from .models import CharacterModel
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CharacterManager:
    """Manages character data for the comic project with session-based storage."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        logger.info("CharacterManager initialized")
    
    def _get_session(self, session_id: str) -> Dict:
        """Get or create a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'characters': [],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'confirmed': False,
                    'version': 1
                }
            }
            logger.info(f"Created new session: {session_id}")
        return self.sessions[session_id]
    
    def extract_characters_from_summary(self, story_text: str) -> List[Dict]:
        """
        Extract characters from story summary using LLM.
        
        Args:
            story_text: The story summary to analyze
            
        Returns:
            List of validated character dictionaries
        """
        logger.info("Starting character extraction from summary")
        
        prompt = (
            "You are an intelligent assistant designed to extract fictional character data from story summaries.\n"
            "Given a short story or summary text, identify the main characters and output their structured details in JSON format.\n"
            "Output Format:\n"
            "[{\"name\": \"Lina Voss\", \"role\": \"protagonist\", \"appearance\": \"A young woman...\", \"booru_tags\": \"silver hair, green eyes, long red coat, mechanical crossbow\"}]\n"
            "Be concise, vivid, and include at least 3 tags per character.\n\n"
            f"STORY:\n{story_text}"
        )
        
        try:
            raw_characters = call_llm_json(prompt)
            if not raw_characters:
                logger.error("LLM returned no valid characters")
                return []
            
            validated_chars = normalize_character_list(raw_characters)
            for c in raw_characters:
                if normalize_character_dict(c) is None:
                    logger.warning(f"Rejected invalid character: {c}")
            
            logger.info(f"Extracted {len(validated_chars)} valid characters")
            return validated_chars
            
        except Exception as e:
            logger.error(f"Character extraction failed: {str(e)}")
            return []
    
    def regenerate_booru_tags(self, appearance_text: str) -> str:
        """
        Regenerate booru tags from character appearance using LLM.
        
        Args:
            appearance_text: The character's appearance description
            
        Returns:
            Comma-separated string of booru tags
        """
        logger.info("Regenerating booru tags from appearance")
        
        prompt = (
            "You are a visual tag generator.\n"
            "Given a character appearance description, return a comma-separated list of booru-style visual tags.\n"
            "Focus especially on physical appearance, facial features, body type, ethnicity, skin color, and gender.\n"
            "Use short, 2–4 word phrases like: 'curly red hair, black jacket, robotic eye'.\n"
            "Do not include emotions or abstract traits.\n\n"
            f"APPEARANCE: {appearance_text}"
        )
        
        try:
            tags = call_llm(prompt)
            # Clean up the response
            tags = tags.replace('\n', ' ').strip()
            if tags.startswith('"') and tags.endswith('"'):
                tags = tags[1:-1]
            
            logger.info(f"Generated {len(tags.split(','))} booru tags")
            return tags
            
        except Exception as e:
            logger.error(f"Tag regeneration failed: {str(e)}")
            return ""
    
    def set_characters(self, session_id: str, characters: List[Dict]) -> bool:
        """Set the complete character list for a session."""
        try:
            session = self._get_session(session_id)
            session['characters'] = characters
            session['metadata']['last_updated'] = datetime.now().isoformat()
            session['metadata']['version'] += 1
            logger.info(f"Set {len(characters)} characters for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting characters: {str(e)}")
            return False
    
    def get_characters(self, session_id: str) -> List[Dict]:
        """Get all characters for a session."""
        session = self._get_session(session_id)
        return session['characters']
    
    def add_character(self, session_id: str, character: Dict) -> Optional[str]:
        """Add a new character to the session."""
        try:
            session = self._get_session(session_id)
            character_id = str(uuid4())
            character['id'] = character_id
            session['characters'].append(character)
            session['metadata']['last_updated'] = datetime.now().isoformat()
            session['metadata']['version'] += 1
            logger.info(f"Added character {character.get('name', 'unnamed')} to session {session_id}")
            return character_id
        except Exception as e:
            logger.error(f"Error adding character: {str(e)}")
            return None
    
    def update_character(self, session_id: str, character_id: str, updates: Dict) -> bool:
        """Update an existing character."""
        try:
            session = self._get_session(session_id)
            for character in session['characters']:
                if character.get('id') == character_id:
                    character.update(updates)
                    session['metadata']['last_updated'] = datetime.now().isoformat()
                    session['metadata']['version'] += 1
                    logger.info(f"Updated character {character.get('name', 'unnamed')} in session {session_id}")
                    return True
            logger.warning(f"Character {character_id} not found in session {session_id}")
            return False
        except Exception as e:
            logger.error(f"Error updating character: {str(e)}")
            return False
    
    def delete_character(self, session_id: str, character_id: str) -> bool:
        """Delete a character from the session."""
        try:
            session = self._get_session(session_id)
            session['characters'] = [c for c in session['characters'] if c.get('id') != character_id]
            session['metadata']['last_updated'] = datetime.now().isoformat()
            session['metadata']['version'] += 1
            logger.info(f"Deleted character {character_id} from session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting character: {str(e)}")
            return False
    
    def confirm_characters(self, session_id: str) -> bool:
        """Lock the character roster for a session."""
        try:
            session = self._get_session(session_id)
            session['metadata']['confirmed'] = True
            session['metadata']['last_updated'] = datetime.now().isoformat()
            logger.info(f"Confirmed character roster for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error confirming characters: {str(e)}")
            return False
    
    def is_confirmed(self, session_id: str) -> bool:
        """Check if the character roster is confirmed."""
        session = self._get_session(session_id)
        return session['metadata']['confirmed']
    
    def reset_confirmation(self, session_id: str) -> bool:
        """Reset the confirmation status for testing purposes."""
        try:
            session = self._get_session(session_id)
            session['metadata']['confirmed'] = False
            session['metadata']['last_updated'] = datetime.now().isoformat()
            logger.info(f"Reset confirmation status for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error resetting confirmation: {str(e)}")
            return False
    
    def export_characters(self, session_id: str) -> Optional[Dict]:
        """Export the character roster with metadata."""
        try:
            session = self._get_session(session_id)
            export_data = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'characters': session['characters'],
                'metadata': session['metadata']
            }
            logger.info(f"Exported character roster for session {session_id}")
            return export_data
        except Exception as e:
            logger.error(f"Error exporting characters: {str(e)}")
            return None
    
    def save_to_file(self, session_id: str, filepath: str) -> bool:
        """Save the character roster to a JSON file."""
        try:
            export_data = self.export_characters(session_id)
            if export_data:
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2)
                logger.info(f"Saved character roster to {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving to file: {str(e)}")
            return False

def normalize_character_dict(raw_char):
    required_fields = ['name', 'role', 'appearance', 'booru_tags']
    # Validate required fields
    for field in required_fields:
        if field not in raw_char or not isinstance(raw_char[field], str) and not (field == 'booru_tags' and isinstance(raw_char[field], list)):
            logger.warning(f"Rejected invalid character: {raw_char}")
            return None
    # Normalize booru_tags
    booru_tags = raw_char['booru_tags']
    if isinstance(booru_tags, list):
        booru_tags = ', '.join(str(tag).strip() for tag in booru_tags)
    elif isinstance(booru_tags, str):
        booru_tags = booru_tags.strip()
    else:
        logger.warning(f"Rejected invalid character: {raw_char}")
        return None
    # Normalize and fill fields
    normalized = {
        'name': str(raw_char['name']).strip(),
        'role': str(raw_char['role']).strip(),
        'appearance': str(raw_char['appearance']).strip(),
        'booru_tags': booru_tags,
        'id': raw_char.get('id') or str(uuid.uuid4()),
        'source': raw_char.get('source', 'LLM'),
        'confirmed': raw_char.get('confirmed', False)
    }
    # Validate again
    for field in required_fields:
        if not normalized[field]:
            logger.warning(f"Rejected invalid character: {raw_char}")
            return None
    return normalized

def normalize_character_list(raw_list):
    valid = []
    for c in raw_list:
        norm = normalize_character_dict(c)
        if norm is not None:
            valid.append(norm)
    return valid 