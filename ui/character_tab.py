import gradio as gr
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
from backend.character_manager import CharacterManager, normalize_character_dict
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CharacterTab:
    """UI component for managing comic characters."""
    
    def __init__(self, character_manager: CharacterManager):
        self.character_manager = character_manager
        self.current_session_id: Optional[str] = None
        logger.info("CharacterTab initialized")
    
    def _create_character_block(self, character: Optional[Dict] = None) -> gr.Blocks:
        """Create a block for a single character's editable fields."""
        with gr.Blocks() as block:
            with gr.Row():
                name = gr.Textbox(
                    label="Name",
                    value=character.get('name', '') if character else '',
                    interactive=True
                )
                role = gr.Textbox(
                    label="Role",
                    value=character.get('role', '') if character else '',
                    interactive=True
                )
                if character and character.get('source') == 'LLM':
                    gr.Markdown("🔹 LLM")
            appearance = gr.Textbox(
                label="Appearance",
                value=character.get('appearance', '') if character else '',
                interactive=True
            )
            with gr.Row():
                booru_tags = gr.Textbox(
                    label="Booru Tags",
                    value=character.get('booru_tags', '') if character else '',
                    interactive=True
                )
                regenerate_btn = gr.Button("Regenerate Tags")
            character_id = gr.Textbox(
                value=character.get('id', '') if character else '',
                visible=False
            )
            
            # Tag regeneration handler
            def regenerate_tags(appearance_text: str) -> str:
                logger.info(f"Regenerating tags for character with appearance: {appearance_text[:50]}...")
                return self.character_manager.regenerate_booru_tags(appearance_text)
            
            regenerate_btn.click(
                fn=regenerate_tags,
                inputs=[appearance],
                outputs=[booru_tags]
            )
            
        return block
    
    def _update_character_ui(self, characters: List[Dict]) -> List[gr.Blocks]:
        """Update the UI with current character blocks."""
        logger.info(f"Updating UI with {len(characters)} characters")
        return [self._create_character_block(char) for char in characters]
    
    def _handle_character_extraction(self, story_summary: str, overwrite: bool) -> tuple[List[Dict], str]:
        """
        Extract characters from story summary using LLM.
        
        Args:
            story_summary: The story summary to analyze
            overwrite: Whether to overwrite existing characters
            
        Returns:
            Tuple of (extracted characters, status message)
        """
        logger.info("Starting character extraction from summary")
        
        try:
            # Extract characters
            characters = self.character_manager.extract_characters_from_summary(story_summary)
            
            if not characters:
                logger.warning("No characters extracted from summary")
                return [], "❌ Extraction failed. Check story input."
            
            # Handle existing characters
            existing = self.character_manager.get_characters(self.current_session_id)
            if existing and not overwrite:
                logger.info(f"Appending {len(characters)} new characters to existing {len(existing)}")
                characters = existing + characters
            elif existing and overwrite:
                logger.info(f"Overwriting {len(existing)} existing characters with {len(characters)} new ones")
            
            # Update session
            self.character_manager.set_characters(self.current_session_id, characters)
            
            # Log normalized characters for debugging
            logger.info(f"Characters to display in table: {characters}")
            
            # Return status message
            if len(characters) >= 3:
                status = f"✅ Successfully extracted {len(characters)} characters."
            else:
                status = f"⚠️ Only {len(characters)} characters extracted. Check summary completeness."
            
            logger.info(status)
            return characters, status
            
        except Exception as e:
            logger.error(f"Character extraction failed: {str(e)}")
            return [], f"❌ Extraction failed: {str(e)}"
    
    def _handle_character_update(self, session_id: str, character_id: str, updates: Dict) -> bool:
        """Update a character's data."""
        logger.info(f"Updating character {character_id} in session {session_id}")
        return self.character_manager.update_character(session_id, character_id, updates)
    
    def _handle_character_delete(self, session_id: str, character_id: str) -> bool:
        """Delete a character."""
        logger.info(f"Deleting character {character_id} from session {session_id}")
        return self.character_manager.delete_character(session_id, character_id)
    
    def _handle_roster_confirmation(self, session_id: str) -> bool:
        """Confirm the character roster."""
        logger.info(f"Confirming roster for session {session_id}")
        return self.character_manager.confirm_characters(session_id)
    
    def create_ui(self) -> gr.Blocks:
        """Create a clean, user-friendly character management UI with all key features, status/debug lines, and user tips."""
        with gr.Blocks(title="Character Management") as ui:
            # --- Status and Instructions ---
            status = gr.Textbox(label="Status", value="🟡 Editable", interactive=False)
            info_line = gr.Markdown(
                """
                **Instructions:**
                - Edit your characters below. Click **Confirm Roster** when ready.
                - You can load characters from JSON, or extract them from your story.
                - After confirming, the roster is locked and can be exported as JSON.
                """,
                visible=True
            )
            tips = gr.Markdown(
                """
                **Tips & Examples:**
                - Example character JSON:
                ```json
                [
                  {"name": "Kira Ashwood", "role": "protagonist", "appearance": "A tall woman with short black hair...", "booru_tags": "1girl, short black hair, pilot suit"}
                ]
                ```
                - You can paste multiple characters in the JSON array.
                - Use the table below to edit details before confirming.
                """,
                visible=True
            )

            # --- Load Characters from JSON ---
            with gr.Row():
                json_input = gr.Textbox(
                    label="Load Characters from JSON",
                    placeholder="Paste your character JSON here",
                    lines=5
                )
                load_json_btn = gr.Button("Load JSON")
            json_load_status = gr.Markdown("", visible=True)

            # --- Editable Character Table ---
            columns = ["name", "role", "appearance", "booru_tags", "source"]
            character_table = gr.Dataframe(
                headers=columns,
                value=[["" for _ in columns]],
                label="Character Roster (Edit fields, then click Confirm)",
                interactive=True
            )
            table_status = gr.Markdown("", visible=True)

            # --- Confirm Roster ---
            with gr.Row():
                refresh_btn = gr.Button("Refresh Table")
                confirm_roster_btn = gr.Button("Confirm Roster")
            confirm_status = gr.Markdown("", visible=True)

            # --- Export/Inspect ---
            export_json_btn = gr.Button("Export Confirmed Roster (Show JSON)")
            export_json_output = gr.Textbox(label="Exported JSON", lines=10, interactive=False)

            # --- Handlers ---
            def load_from_json(json_str: str) -> tuple:
                try:
                    characters = json.loads(json_str)
                    if not isinstance(characters, list):
                        return [], "❌ Invalid JSON: Expected a list of characters"
                    valid_chars = []
                    for char in characters:
                        norm = normalize_character_dict(char)
                        if norm:
                            valid_chars.append(norm)
                    if not valid_chars:
                        return [], "❌ No valid characters found in JSON"
                    self.character_manager.set_characters(self.current_session_id, valid_chars)
                    return valid_chars, f"✅ Successfully loaded {len(valid_chars)} characters. Edit below and confirm when ready."
                except json.JSONDecodeError:
                    return [], "❌ Invalid JSON format"
                except Exception as e:
                    logger.error(f"Error loading JSON: {str(e)}")
                    return [], f"❌ Error loading JSON: {str(e)}"

            def get_character_table(session_id):
                chars = self.character_manager.get_characters(session_id)
                logger.info(f"[DEBUG] Table - session_id: {session_id}")
                logger.info(f"[DEBUG] Table - characters fetched: {chars}")
                if not chars:
                    return [], 0
                data = [[c.get(col, "") for col in columns] for c in chars]
                return data, len(chars)

            def refresh_table(session_id):
                data, count = get_character_table(session_id)
                status_msg = f"Loaded {count} characters for session: {session_id}. Characters are editable. Please review and click 'Confirm Roster' when ready."
                return data, status_msg

            def on_confirm(table_data, session_id):
                expected_columns = 5
                columns = ["name", "role", "appearance", "booru_tags", "source"]
                if hasattr(table_data, "values"):
                    table_data = table_data.values.tolist()
                elif isinstance(table_data, dict):
                    table_data = list(table_data.values())
                def sanitize_character_row(row, expected_columns=5):
                    if not isinstance(row, list):
                        logger.warning(f"Non-list row found: {row}")
                        return None
                    if row == columns:
                        logger.warning(f"Skipping header row: {row}")
                        return None
                    if len(row) < expected_columns:
                        logger.warning(f"Row too short: {row}, padding to length {expected_columns}")
                        row = row + ["" for _ in range(expected_columns - len(row))]
                    elif len(row) > expected_columns:
                        logger.warning(f"Row too long: {row}, trimming to {expected_columns}")
                        row = row[:expected_columns]
                    return row
                valid_chars = []
                start_idx = 1 if len(table_data) > 0 and table_data[0] == columns else 0
                for idx, row in enumerate(table_data[start_idx:], start=start_idx):
                    sanitized = sanitize_character_row(row, expected_columns)
                    if sanitized is None:
                        logger.warning(f"Skipping invalid row at index {idx}: {row}")
                        continue
                    name, role, appearance, booru_tags, source = sanitized
                    if (
                        name and len(name.strip()) > 1 and
                        role and len(role.strip()) > 1 and
                        (
                            (appearance and len(appearance.strip()) > 1) or
                            (booru_tags and len(booru_tags.strip()) > 1) or
                            (source and len(str(source).strip()) > 1)
                        )
                    ):
                        character_dict = {
                            'name': name.strip(),
                            'role': role.strip(),
                            'appearance': appearance.strip(),
                            'booru_tags': booru_tags.strip(),
                            'source': source.strip() if source else 'LLM',
                            'id': str(uuid.uuid4())
                        }
                        valid_chars.append(character_dict)
                    else:
                        logger.info(f"Skipping invalid/empty row at index {idx}: {sanitized}")
                if valid_chars:
                    self.character_manager.set_characters(session_id, valid_chars)
                    self.character_manager.confirm_characters(session_id)
                    status_msg = f"✅ Successfully saved and confirmed {len(valid_chars)} characters. Roster is now locked."
                else:
                    status_msg = "⚠️ No valid characters to save"
                data, _ = refresh_table(session_id)
                return "✅ Confirmed", status_msg, data, status_msg

            def export_confirmed_json():
                try:
                    chars = self.character_manager.get_characters(self.current_session_id)
                    return json.dumps(chars, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.error(f"Error exporting confirmed JSON: {str(e)}")
                    return f"❌ Error exporting JSON: {str(e)}"

            # --- Button Click Handlers ---
            load_json_btn.click(
                fn=load_from_json,
                inputs=[json_input],
                outputs=[character_table, json_load_status]
            )
            session_id_box = gr.Textbox(value=self.current_session_id or "", visible=False)
            refresh_btn.click(
                fn=refresh_table,
                inputs=[session_id_box],
                outputs=[character_table, table_status]
            )
            confirm_roster_btn.click(
                fn=on_confirm,
                inputs=[character_table, session_id_box],
                outputs=[status, confirm_status, character_table, table_status]
            )
            export_json_btn.click(
                fn=export_confirmed_json,
                inputs=[],
                outputs=[export_json_output]
            )

        logger.info("Created clean character management UI (single editable table, confirm to save, with debug/status info, and user tips)")
        return ui
    
    def set_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.current_session_id = session_id
        logger.info(f"Set current session to {session_id}")
    
    def get_characters(self) -> List[Dict]:
        """Get all characters for the current session."""
        if not self.current_session_id:
            logger.warning("No session ID set")
            return []
        return self.character_manager.get_characters(self.current_session_id) 