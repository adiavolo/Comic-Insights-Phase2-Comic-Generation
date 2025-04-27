import requests
import json
import base64
import os
from datetime import datetime
import logging
from core.logging_config import track_status
from typing import Tuple, Optional, Dict, Any

class ImageGenerationError(Exception):
    pass

class ImageAPI:
    def __init__(self):
        self.logger = logging.getLogger('comic_insights.debug')
        self.status_logger = logging.getLogger('comic_insights.status')
        self.error_logger = logging.getLogger('comic_insights.error')
        
        # Initialize debug logging
        self.logger.debug("Initializing ImageAPI")
        
        # Get the absolute path to the project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(self.project_root, 'config', 'styles.json')
        
        with open(config_path) as f:
            self.config = json.load(f)
        self.api_endpoint = self.config['api_endpoint']
        self.stabilizer_lora = self.config.get('stabilizer_lora', '')
        self.negative_embedding = self.config.get('negative_embedding', '')
        self.ensure_export_dir()

    def ensure_export_dir(self):
        """Ensure the export directory exists"""
        export_dir = os.path.join(self.project_root, 'export')
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def _log_generation_params(self, params: Dict[str, Any]):
        """Log generation parameters for debugging"""
        self.logger.debug(f"Generation parameters: {json.dumps(params, indent=2)}")

    def _validate_dimensions(self, width: int, height: int) -> Tuple[bool, str]:
        """Validate image dimensions"""
        if width <= 0 or height <= 0:
            return False, "Dimensions must be positive"
        if width > 1536 or height > 1536:
            return False, "Dimensions cannot exceed 1536 pixels"
        return True, ""

    @track_status("ImageGeneration")
    def generate_image(self, prompt: str, style: Dict[str, Any], cfg_scale: float,
                      negative_prompt: str = "", width: int = 512, height: int = 512) -> Tuple[str, str]:
        """Generate an image with comprehensive logging and status tracking"""
        try:
            # Log generation attempt
            self.logger.info(f"Starting image generation with prompt: {prompt[:50]}...")
            
            # Validate inputs
            if not prompt:
                raise ValueError("Prompt cannot be empty")
            
            valid_dims, error_msg = self._validate_dimensions(width, height)
            if not valid_dims:
                raise ValueError(f"Invalid dimensions: {error_msg}")
            
            # Log generation parameters
            params = {
                'prompt': prompt,
                'style': style,
                'cfg_scale': cfg_scale,
                'negative_prompt': negative_prompt,
                'width': width,
                'height': height,
                'timestamp': datetime.now().isoformat()
            }
            self._log_generation_params(params)
            
            # Compose LoRA and prompt additions
            lora_str = ' '.join(style.get('lora', []))
            prompt_add = style.get('prompt_add', '')
            # Always add the stabilizer LoRA
            lora_full = f"{lora_str} {self.stabilizer_lora}".strip()
            # Compose the full prompt
            full_prompt = f"{prompt}, {prompt_add} {lora_full}".strip()
            # Add lazyneg to negative prompt
            neg_prompt = f"{negative_prompt} {self.negative_embedding}".strip()
            # Prepare the payload
            payload = {
                "prompt": full_prompt,
                "negative_prompt": neg_prompt,
                "cfg_scale": cfg_scale,
                "sampler_name": "DPM++ 2M SDE",
                "steps": 23,
                "width": width,
                "height": height
            }
            print("[Comic Insights] Payload sent to SD API:")
            print(json.dumps(payload, indent=2))
            # Make the API request
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            
            # Extract the image data
            result = response.json()
            image_data = result["images"][0]
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(self.project_root, 'export', f'generated_{timestamp}.png')
            
            # Decode and save the base64 image
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            
            # Log successful generation
            self.logger.info(f"Successfully generated image: {image_path}")
            
            return image_path, full_prompt

        except requests.exceptions.RequestException as e:
            # Log error with full context
            self.error_logger.exception(
                "API request failed",
                extra={
                    'prompt': prompt,
                    'style': style,
                    'dimensions': f"{width}x{height}",
                    'error': str(e)
                }
            )
            raise ImageGenerationError(f"API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            # Log error with full context
            self.error_logger.exception(
                "Invalid API response",
                extra={
                    'prompt': prompt,
                    'style': style,
                    'dimensions': f"{width}x{height}",
                    'error': str(e)
                }
            )
            raise ImageGenerationError(f"Invalid API response: {str(e)}")
        except Exception as e:
            # Log error with full context
            self.error_logger.exception(
                "Image generation failed",
                extra={
                    'prompt': prompt,
                    'style': style,
                    'dimensions': f"{width}x{height}",
                    'error': str(e)
                }
            )
            raise ImageGenerationError(f"Image generation failed: {str(e)}")

    @track_status("ImageProcessing")
    def process_image(self, image_path: str, operation: str, params: Dict[str, Any]) -> str:
        """Process an existing image with logging"""
        try:
            self.logger.info(f"Processing image {image_path} with operation: {operation}")
            self.logger.debug(f"Processing parameters: {json.dumps(params, indent=2)}")
            
            # TODO: Implement image processing logic
            processed_path = f"processed_{image_path}"
            
            self.logger.info(f"Image processing completed: {processed_path}")
            return processed_path
            
        except Exception as e:
            self.error_logger.exception(
                "Image processing failed",
                extra={
                    'image_path': image_path,
                    'operation': operation,
                    'params': params,
                    'error': str(e)
                }
            )
            raise 