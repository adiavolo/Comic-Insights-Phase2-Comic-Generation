import json
import os
from backend.character_manager import CharacterManager

def test_manual_roster():
    # Initialize character manager
    character_manager = CharacterManager()
    test_session_id = "manual_test_session"
    
    # Load test character data
    test_data_path = os.path.join(os.path.dirname(__file__), 'test_character_data.json')
    if not os.path.exists(test_data_path):
        print(f"❌ Test data file not found at: {test_data_path}")
        return
    
    try:
        # Load the characters
        with open(test_data_path, 'r') as f:
            test_characters = json.load(f)
        print(f"✓ Loaded {len(test_characters)} characters from test data")
        
        # Set the characters in the session
        success = character_manager.set_characters(test_session_id, test_characters)
        if not success:
            print("❌ Failed to set characters")
            return
        print("✓ Characters set in session")
        
        # Verify characters were set
        characters = character_manager.get_characters(test_session_id)
        print(f"✓ Retrieved {len(characters)} characters from session")
        
        # Confirm the roster
        success = character_manager.confirm_characters(test_session_id)
        if not success:
            print("❌ Failed to confirm roster")
            return
        print("✓ Roster confirmed")
        
        # Verify confirmation status
        is_confirmed = character_manager.is_confirmed(test_session_id)
        print(f"✓ Confirmation status: {is_confirmed}")
        
        # Export the data to verify
        export_file = "manual_test_export.json"
        success = character_manager.save_to_file(test_session_id, export_file)
        if not success:
            print("❌ Failed to export data")
            return
        print(f"✓ Data exported to {export_file}")
        
        # Print the exported data
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        print("\nExported Data Summary:")
        print(f"Session ID: {exported_data['session_id']}")
        print(f"Number of characters: {len(exported_data['characters'])}")
        print(f"Confirmed: {exported_data['metadata']['confirmed']}")
        print(f"Last updated: {exported_data['metadata']['last_updated']}")
        
        # Clean up
        os.remove(export_file)
        print("\n✓ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_manual_roster() 