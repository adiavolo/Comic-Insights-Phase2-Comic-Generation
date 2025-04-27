"""Story tab component for Comic Insights.

This module handles the story planning and management interface, providing tools for:
- Story prompt creation: Define and refine story concepts
- Plot structure visualization: Organize story elements visually
- Scene flow management: Plan and arrange comic scenes

The tab provides a foundation for:
1. Creating detailed story prompts
2. Managing plot elements and structure
3. Organizing scenes and story flow
4. Future AI-assisted story development

Technical Implementation:
- Uses Gradio components for the UI
- Implements error handling and logging
- Provides status tracking for operations
- Supports custom configuration via StoryTabConfig
"""

import gradio as gr
import logging
from typing import Tuple
from dataclasses import dataclass
from ..utils.logging_utils import ComponentLogger
from ..utils.status_tracker import track_status

logger = ComponentLogger(__name__)

@dataclass
class StoryTabConfig:
    """Configuration for Story Tab appearance and behavior
    
    Attributes:
        prompt_lines (int): Number of lines in the prompt input field
        prompt_placeholder (str): Default text shown in the prompt field
        prompt_info (str): Help text shown below the prompt field
        coming_soon_features (list[str]): List of planned future features
    """
    prompt_lines: int = 4
    prompt_placeholder: str = "Enter your story prompt or scene description here..."
    prompt_info: str = "Describe your comic's story or scene in detail."
    coming_soon_features: list[str] = (
        "AI-powered story structure suggestions",  # Smart plot assistance
        "Character relationship mapping",          # Visual character connections
        "Scene flow visualization"                 # Interactive scene planning
    )

class StoryTab:
    """Story tab component implementation
    
    This class manages the UI components and logic for the story planning tab.
    It provides an interface for creating and managing comic story elements,
    including prompts, plot structure, and scene organization.
    """
    
    def __init__(self, config: StoryTabConfig = None):
        """Initialize Story tab with optional custom configuration
        
        Args:
            config (StoryTabConfig, optional): Custom configuration for the tab.
                If not provided, uses default configuration.
        """
        self.config = config or StoryTabConfig()
        self.logger = logger
        self.components = None  # Will store (prompt, button, output) tuple
    
    @track_status("StoryTab")
    def create(self) -> Tuple[gr.Textbox, gr.Button, gr.Markdown]:
        """Create and return the Story tab components
        
        Creates a complete UI for story planning, including:
        - Story prompt input
        - Summary generation button
        - Output display area
        - Coming soon features section
        
        Returns:
            Tuple[gr.Textbox, gr.Button, gr.Markdown]: Story components
                - story_prompt: Text input for story description
                - story_summary_btn: Button to generate summary
                - story_output: Display area for generated content
        """
        try:
            with gr.Column():
                # Story input section
                gr.Markdown("## Story Setup")
                story_prompt = gr.Textbox(
                    label="Story Prompt",
                    placeholder=self.config.prompt_placeholder,
                    lines=self.config.prompt_lines,
                    info=self.config.prompt_info
                )
                
                # Control section
                story_summary_btn = gr.Button(
                    "Generate Story Summary",
                    interactive=False,  # Will be enabled with backend
                    variant="secondary"
                )
                
                # Output section
                story_output = gr.Markdown(
                    "*Story summary will appear here after backend connection*"
                )
                
                # Future features section
                gr.Markdown("### Coming Soon:")
                features_list = "\n".join(
                    f"- {feature}" for feature in self.config.coming_soon_features
                )
                gr.Markdown(features_list)
            
            self.components = (story_prompt, story_summary_btn, story_output)
            self.logger.info("Successfully created story tab components")
            return self.components
            
        except Exception as e:
            self.logger.error(f"Failed to create story tab: {str(e)}")
            raise
    
    def attach_handlers(self):
        """Attach event handlers to story tab components
        
        Sets up the event handling for:
        - Summary generation
        - Input validation
        - Output processing
        
        Note: This is a placeholder for future implementation
        
        Raises:
            RuntimeError: If called before components are created
        """
        if not self.components:
            raise RuntimeError("Components not created. Call create() first.")
        
        # Future handler implementation will go here
        pass 