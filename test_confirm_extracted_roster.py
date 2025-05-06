from backend.character_manager import CharacterManager

# Set your session ID and story summary here
session_id = "extracted_test_session"
story_summary = """
A mysterious city floats above the clouds, ruled by a council of enigmatic figures. Kira Ashwood, a daring pilot, seeks to uncover the secrets of the city with the help of her mentor, Ravi Thorne, and her rival, Ayaka Kisaragi. Along the way, they encounter Mira Solenne, a shadowy antagonist, and Eli Draven, a quirky hacker. The group is watched by Nyra, a cloaked observer with unknown motives.
"""

character_manager = CharacterManager()

# 1. Extract characters
characters = character_manager.extract_characters_from_summary(story_summary)
print(f"Extracted {len(characters)} characters.")

# 2. Set characters in session
character_manager.set_characters(session_id, characters)

# 3. Confirm the roster
character_manager.confirm_characters(session_id)

# 4. Save to JSON file
export_path = "extracted_roster.json"
character_manager.save_to_file(session_id, export_path)
print(f"Roster confirmed and saved to {export_path}") 