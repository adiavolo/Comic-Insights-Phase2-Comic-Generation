import requests
import json
import base64
import os
from datetime import datetime

class ImageGenerationError(Exception):
    pass

class ImageAPI:
    def __init__(self):
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

    def generate_image(self, prompt, style, cfg_scale, negative_prompt="", width=512, height=512):
        """
        Generate an image using the Stable Diffusion API
        Returns the path to the saved image
        """
        try:
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
            
            return image_path, full_prompt

        except requests.exceptions.RequestException as e:
            raise ImageGenerationError(f"API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise ImageGenerationError(f"Invalid API response: {str(e)}")
        except Exception as e:
            raise ImageGenerationError(f"Image generation failed: {str(e)}") 