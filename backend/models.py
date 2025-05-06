from pydantic import BaseModel, Field
from typing import Optional

class CharacterModel(BaseModel):
    """Schema for character data with validation."""
    
    name: str = Field(..., description="Character's name or nickname")
    role: str = Field(..., description="Character's role in the story")
    appearance: str = Field(..., description="Visual description of the character")
    booru_tags: str = Field(..., description="Comma-separated visual tags for the character")
    source: str = Field(default="LLM", description="Source of the character data")
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "appearance": self.appearance,
            "booru_tags": self.booru_tags,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Optional['CharacterModel']:
        """Create model from dictionary with error handling."""
        try:
            return cls(**data)
        except Exception as e:
            return None 