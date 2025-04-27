import pandas as pd
import os
import json

class PromptManager:
    def __init__(self, config_path, custom_styles_path):
        """Initialize the PromptManager with style configurations"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.project_root, config_path)
        self.custom_styles_path = os.path.join(self.project_root, 'config', 'styles', custom_styles_path)
        
        # Load configurations
        self._load_configs()
    
    def _load_configs(self):
        """Load all style configurations"""
        # Load base styles from JSON
        with open(self.config_path) as f:
            config = json.load(f)
            self.base_styles = config['styles']
            self.aspect_ratios = config['aspect_ratios']
        
        # Load custom styles from CSV
        self.custom_styles_df = pd.read_csv(self.custom_styles_path)
        self.custom_styles = self.custom_styles_df.to_dict('records')
    
    def get_base_style_names(self):
        """Get list of base style names"""
        return [s['name'] for s in self.base_styles]
    
    def get_custom_style_names(self):
        """Get list of custom style names"""
        return [s['name'] for s in self.custom_styles]
    
    def get_aspect_ratio_names(self):
        """Get list of aspect ratio names"""
        return [ar['name'] for ar in self.aspect_ratios]
    
    def get_base_style(self, style_name):
        """Get base style configuration by name"""
        return next((s for s in self.base_styles if s['name'] == style_name), self.base_styles[0])
    
    def get_aspect_ratio(self, aspect_ratio_name):
        """Get aspect ratio configuration by name"""
        return next((ar for ar in self.aspect_ratios if ar['name'] == aspect_ratio_name), self.aspect_ratios[0])
    
    def get_custom_style(self, style_name):
        """Get custom style configuration by name"""
        return next((s for s in self.custom_styles if s['name'] == style_name), None)
    
    def build_prompt(self, user_prompt, base_style_name, custom_style_names=None):
        """Build the final prompt combining user input, base style, and custom styles"""
        # Get base style
        base_style = self.get_base_style(base_style_name)
        
        # Initialize prompt parts
        prompt_parts = [user_prompt]  # Start with user prompt
        negative_prompt_parts = []
        
        # Add custom styles first
        if custom_style_names:
            for style_name in custom_style_names:
                custom_style = self.get_custom_style(style_name)
                if custom_style:
                    # Format the custom style prompt with the user prompt
                    formatted_prompt = custom_style['prompt'].format(prompt=user_prompt)
                    prompt_parts.append(formatted_prompt)
                    if custom_style['negative_prompt'] and not pd.isna(custom_style['negative_prompt']):
                        negative_prompt_parts.append(str(custom_style['negative_prompt']))
        
        # Add base style
        prompt_parts.append(base_style['prompt_add'])
        
        # Combine prompts
        final_prompt = ", ".join(prompt_parts)  # Use comma separation for better prompt organization
        final_negative_prompt = ", ".join(negative_prompt_parts) if negative_prompt_parts else ""
        
        return final_prompt, final_negative_prompt 