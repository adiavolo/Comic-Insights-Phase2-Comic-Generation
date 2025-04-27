"""Image Generation and Editing tab component for Comic Insights.

This module handles image generation and editing features:
- Prompt-based image generation: Create images from textual descriptions
- Image editing and refinement: Modify and enhance generated images
- Style consistency management: Maintain visual coherence across generations
- Export and format handling: Save and convert images in various formats

The tab provides an intuitive interface for:
1. Entering detailed prompts for image generation
2. Specifying elements to avoid using negative prompts
3. Adjusting image dimensions and style presets
4. Viewing and saving generated results

Technical Implementation:
- Uses Gradio components for the UI
- Implements error handling and logging
- Provides status tracking for operations
- Supports custom configuration via ImageTabConfig
"""

import gradio as gr
import logging
from typing import Tuple, Callable, Any
from dataclasses import dataclass, field
from ..utils.logging_utils import ComponentLogger
from ..utils.status_tracker import track_status

logger = ComponentLogger(__name__)

@dataclass
class ImageTabConfig:
    """Configuration for Image Generation Tab appearance and behavior
    
    Attributes:
        prompt_placeholder (str): Default text shown in the prompt input field
        negative_prompt_placeholder (str): Default text shown in the negative prompt field
        default_width (int): Default width for generated images (in pixels)
        default_height (int): Default height for generated images (in pixels)
        style_presets (list[str]): Available style presets for image generation
    """
    prompt_placeholder: str = "Enter your image generation prompt here..."
    negative_prompt_placeholder: str = "Enter elements to avoid in generation..."
    default_width: int = 512  # Standard stable diffusion size
    default_height: int = 512  # Standard stable diffusion size
    style_presets: list[str] = field(default_factory=lambda: [
        "Manga",      # Japanese comic style
        "Comic Book", # Western comic style
        "Realistic",  # Photorealistic rendering
        "Watercolor"  # Artistic watercolor effect
    ])

class ImageTab:
    """Image generation and editing tab implementation
    
    This class manages the UI components and logic for the image generation tab.
    It provides an interface for creating images from text prompts, adjusting
    generation parameters, and handling the generated outputs.
    """
    
    def __init__(self, config: ImageTabConfig = None):
        """Initialize Image tab with optional custom configuration
        
        Args:
            config (ImageTabConfig, optional): Custom configuration for the tab.
                If not provided, uses default configuration.
        """
        self.config = config or ImageTabConfig()
        self.logger = logger
        self.components = {}  # Stores UI component references
    
    @track_status("ImageTab")
    def create(self, generate_callback: Callable[[str, str, int, int, str], Any]) -> dict:
        """Create and return the Image Generation tab components
        
        Creates a complete UI for image generation, including:
        - Prompt input fields
        - Dimension controls
        - Style selection
        - Generation button
        - Output display
        
        Args:
            generate_callback: Function to handle image generation
                Expected signature: (prompt, negative_prompt, width, height, style) -> image
            
        Returns:
            dict: Dictionary containing references to all created UI components
                Keys:
                - prompt: Main prompt input
                - negative_prompt: Negative prompt input
                - width: Image width slider
                - height: Image height slider
                - style: Style preset dropdown
                - generate_btn: Generation trigger button
                - output_image: Image display component
        """
        try:
            with gr.Column() as col:
                # Prompt input section
                prompt = gr.Textbox(
                    label="Generation Prompt",
                    placeholder=self.config.prompt_placeholder,
                    lines=3,
                    info="Describe the image you want to generate in detail"
                )
                negative_prompt = gr.Textbox(
                    label="Negative Prompt",
                    placeholder=self.config.negative_prompt_placeholder,
                    lines=2,
                    info="Specify elements you want to avoid in the generation"
                )
                
                # Dimension controls
                with gr.Row():
                    width = gr.Slider(
                        label="Width",
                        minimum=256,  # Minimum stable size
                        maximum=1024, # Maximum recommended size
                        step=64,      # Standard increment
                        value=self.config.default_width
                    )
                    height = gr.Slider(
                        label="Height",
                        minimum=256,
                        maximum=1024,
                        step=64,
                        value=self.config.default_height
                    )
                
                # Style selection
                style = gr.Dropdown(
                    label="Style Preset",
                    choices=self.config.style_presets,
                    value=self.config.style_presets[0],
                    info="Choose the artistic style for your generation"
                )
                
                # Generation controls
                generate_btn = gr.Button("Generate Image", variant="primary")
                
                # Output section
                output_image = gr.Image(
                    label="Generated Image",
                    type="pil",
                    tool="editor"  # Enables basic image editing
                )
                
            # Store component references for event handling
            self.components = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "style": style,
                "generate_btn": generate_btn,
                "output_image": output_image
            }
            
            self.logger.info("Successfully created image generation tab")
            return self.components
            
        except Exception as e:
            self.logger.error(f"Failed to create image tab: {str(e)}")
            raise
    
    def attach_handlers(self):
        """Attach event handlers to image tab components
        
        Sets up the event handling for:
        - Generate button clicks
        - Input validation
        - Output processing
        
        Raises:
            RuntimeError: If called before components are created
        """
        if not self.components:
            raise RuntimeError("Components not created. Call create() first.")
        
        c = self.components
        # Attach click handler to generate button
        c["generate_btn"].click(
            fn=lambda p, n, w, h, s: None,  # Placeholder for actual generation
            inputs=[
                c["prompt"],         # Main prompt text
                c["negative_prompt"], # Elements to avoid
                c["width"],          # Image width
                c["height"],         # Image height
                c["style"]           # Style preset
            ],
            outputs=c["output_image"]
        ) 