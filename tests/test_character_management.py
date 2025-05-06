import unittest
import json
import os
import sys
from datetime import datetime
from backend.character_manager import CharacterManager
from ui.character_tab import CharacterTab

class TestCharacterManagement(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        try:
            self.character_manager = CharacterManager()
            self.character_tab = CharacterTab(self.character_manager)
            self.test_session_id = "test_session_123"
            self.test_character = {
                'name': 'Test Character',
                'role': 'Test Role',
                'appearance': 'Test Appearance',
                'booru_tags': '1girl, test, character'
            }
            
            # Load test character data
            test_data_path = os.path.join(os.path.dirname(__file__), 'test_character_data.json')
            if not os.path.exists(test_data_path):
                raise FileNotFoundError(f"Test data file not found at: {test_data_path}")
            
            with open(test_data_path, 'r') as f:
                self.test_characters = json.load(f)
            
            # Reset confirmation status before each test
            self.character_manager.reset_confirmation(self.test_session_id)
            
            print(f"\nStarting test: {self._testMethodName}")
        except Exception as e:
            print(f"Error in setUp: {str(e)}")
            raise
    
    def test_character_manager_initialization(self):
        """Test character manager initialization."""
        try:
            self.assertIsNotNone(self.character_manager)
            print("✓ Character manager initialized successfully")
        except Exception as e:
            print(f"Error in test_character_manager_initialization: {str(e)}")
            raise
    
    def test_session_management(self):
        """Test session creation and retrieval."""
        try:
            # Test session creation
            session = self.character_manager._get_session(self.test_session_id)
            self.assertIsNotNone(session)
            self.assertEqual(session['metadata']['confirmed'], False)
            print("✓ Session created successfully")
            
            # Test session retrieval
            same_session = self.character_manager._get_session(self.test_session_id)
            self.assertEqual(session, same_session)
            print("✓ Session retrieved successfully")
        except Exception as e:
            print(f"Error in test_session_management: {str(e)}")
            raise
    
    def test_character_crud(self):
        """Test character CRUD operations."""
        try:
            # Create
            character_id = self.character_manager.add_character(
                self.test_session_id,
                self.test_character
            )
            self.assertIsNotNone(character_id)
            print("✓ Character added successfully")
            
            # Read
            characters = self.character_manager.get_characters(self.test_session_id)
            self.assertEqual(len(characters), 1)
            self.assertEqual(characters[0]['name'], self.test_character['name'])
            print("✓ Character retrieved successfully")
            
            # Update
            update_data = {'name': 'Updated Name'}
            success = self.character_manager.update_character(
                self.test_session_id,
                character_id,
                update_data
            )
            self.assertTrue(success)
            updated_characters = self.character_manager.get_characters(self.test_session_id)
            self.assertEqual(updated_characters[0]['name'], 'Updated Name')
            print("✓ Character updated successfully")
            
            # Delete
            success = self.character_manager.delete_character(
                self.test_session_id,
                character_id
            )
            self.assertTrue(success)
            remaining_characters = self.character_manager.get_characters(self.test_session_id)
            self.assertEqual(len(remaining_characters), 0)
            print("✓ Character deleted successfully")
        except Exception as e:
            print(f"Error in test_character_crud: {str(e)}")
            raise
    
    def test_character_tab_ui(self):
        """Test character tab UI functionality."""
        try:
            # Set session
            self.character_tab.set_session(self.test_session_id)
            self.assertEqual(self.character_tab.current_session_id, self.test_session_id)
            print("✓ Session set in character tab")
            
            # Set characters directly instead of extracting
            self.character_manager.set_characters(self.test_session_id, self.test_characters)
            characters = self.character_manager.get_characters(self.test_session_id)
            self.assertEqual(len(characters), len(self.test_characters))
            print("✓ Characters set successfully")
            
            # Test UI creation
            ui = self.character_tab.create_ui()
            self.assertIsNotNone(ui)
            print("✓ UI created successfully")
        except Exception as e:
            print(f"Error in test_character_tab_ui: {str(e)}")
            raise
    
    def test_roster_confirmation(self):
        """Test roster confirmation functionality."""
        try:
            # Add test characters
            self.character_manager.set_characters(self.test_session_id, self.test_characters)
            print(f"✓ Added {len(self.test_characters)} test characters")
            
            # Confirm roster
            success = self.character_manager.confirm_characters(self.test_session_id)
            self.assertTrue(success)
            
            # Check confirmation status
            is_confirmed = self.character_manager.is_confirmed(self.test_session_id)
            self.assertTrue(is_confirmed)
            print("✓ Roster confirmed successfully")
        except Exception as e:
            print(f"Error in test_roster_confirmation: {str(e)}")
            raise
    
    def test_export_functionality(self):
        """Test character export functionality."""
        try:
            # Add test characters
            self.character_manager.set_characters(self.test_session_id, self.test_characters)
            print(f"✓ Added {len(self.test_characters)} test characters")
            
            # Export characters
            export_data = self.character_manager.export_characters(self.test_session_id)
            self.assertIsNotNone(export_data)
            self.assertEqual(export_data['session_id'], self.test_session_id)
            self.assertEqual(len(export_data['characters']), len(self.test_characters))
            print("✓ Characters exported successfully")
            
            # Test file export
            test_file = "test_export.json"
            success = self.character_manager.save_to_file(self.test_session_id, test_file)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(test_file))
            print("✓ File export successful")
            
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
                print("✓ Cleanup successful")
        except Exception as e:
            print(f"Error in test_export_functionality: {str(e)}")
            raise

if __name__ == '__main__':
    # Add current directory to Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run tests with verbosity
    unittest.main(verbosity=2) 