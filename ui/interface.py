import gradio as gr
import os
from datetime import datetime
from backend import img_api, nlp_engine, session_manager
from .prompt_manager import PromptManager

# Initialize backend components
img_generator = img_api.ImageAPI()
nlp = nlp_engine.NLPEngine()
session_mgr = session_manager.SessionManager()

# Initialize prompt manager
prompt_mgr = PromptManager('config/styles.json', 'styles_integrated_filtered.csv')

MAX_DIM = 1536

def calculate_dimensions(aspect, custom_dim, dim_type):
    # aspect: dict with width, height
    # custom_dim: int, the user-supplied dimension
    # dim_type: 'width' or 'height'
    w, h = aspect['width'], aspect['height']
    if dim_type == 'width':
        width = min(custom_dim, MAX_DIM)
        height = int(width * h / w)
        if height > MAX_DIM:
            height = MAX_DIM
            width = int(height * w / h)
    else:
        height = min(custom_dim, MAX_DIM)
        width = int(height * w / h)
        if width > MAX_DIM:
            width = MAX_DIM
            height = int(width * h / w)
    return width, height

def generate_comic(prompt, style_name, cfg_scale, negative_prompt, aspect_ratio_name, custom_dim, dim_type, selected_custom_styles, session_id):
    """Generate comic content based on user inputs"""
    try:
        # Get aspect ratio and calculate dimensions
        aspect = prompt_mgr.get_aspect_ratio(aspect_ratio_name)
        width, height = calculate_dimensions(aspect, custom_dim, dim_type)
        
        # Build prompts
        final_prompt, custom_negative_prompt = prompt_mgr.build_prompt(
            prompt, 
            style_name, 
            selected_custom_styles
        )
        
        # Combine negative prompts
        final_negative_prompt = ", ".join(filter(None, [custom_negative_prompt, negative_prompt]))
        
        # Generate the image
        image, full_prompt_with_lora = img_generator.generate_image(
            prompt=final_prompt,
            style=prompt_mgr.get_base_style(style_name),
            cfg_scale=cfg_scale,
            negative_prompt=final_negative_prompt,
            width=width,
            height=height
        )
        
        # Update session history
        session_mgr.add_entry(
            session_id=session_id,
            prompt=prompt,
            style=style_name,
            image=image,
            plot=final_prompt  # Store the final prompt as plot for now
        )
        
        # Get session history
        history = session_mgr.get_history(session_id)
        
        # Create payload display
        payload_display = f"[Comic Insights] Prompt sent to SD API:\n{full_prompt_with_lora}"
        
        return payload_display, image, history
    except Exception as e:
        raise gr.Error(f"Error generating comic: {str(e)}")

def create_interface():
    """Create and return the Gradio interface"""
    # Create a new session
    session_id = session_mgr.create_session()
    
    with gr.Blocks(title="Comic Insights") as demo:
        gr.Markdown("""
        # Comic Insights
        Welcome to Comic Insights! Generate unique comic pages with AI-powered art and text. 
        1. **Describe your scene** in detail for best results.
        2. **Choose an art style** to set the visual mood.
        3. **Select custom styles** to enhance your generation.
        4. **Pick an aspect ratio** for your comic panel.
        5. **Adjust size** for your comic panel.
        6. **Fine-tune** with CFG scale and negative prompts.
        7. **Export** your creations and view your session history.
        """)
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Comic Scene Setup")
                prompt = gr.Textbox(
                    label="Scene Description",
                    placeholder="Describe your comic scene in detail... (e.g. A futuristic city at night, neon lights, two heroes in battle)",
                    lines=4,
                    info="The more detailed, the better the result!"
                )
                style_name = gr.Dropdown(
                    choices=prompt_mgr.get_base_style_names(),
                    label="Art Style",
                    value=prompt_mgr.get_base_style_names()[0],
                    info="Select the base art style for your comic page."
                )
                custom_styles = gr.Dropdown(
                    choices=prompt_mgr.get_custom_style_names(),
                    label="Custom Styles",
                    value=None,
                    multiselect=True,
                    info="Select additional custom styles to enhance your generation."
                )
                aspect_ratio_name = gr.Dropdown(
                    choices=prompt_mgr.get_aspect_ratio_names(),
                    label="Aspect Ratio",
                    value=prompt_mgr.get_aspect_ratio_names()[0],
                    info="Select the aspect ratio for your comic page."
                )
                dim_type = gr.Radio(
                    choices=["width", "height"],
                    label="Dimension to set",
                    value="width",
                    info="Choose which dimension to set manually. The other will be calculated automatically."
                )
                custom_dim = gr.Number(
                    label="Custom Dimension (px)",
                    value=prompt_mgr.get_aspect_ratio(prompt_mgr.get_aspect_ratio_names()[0])['width'],
                    precision=0,
                    info="Set your preferred width or height in pixels (max 1536)."
                )
                cfg_scale = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=7.5,
                    step=0.5,
                    label="CFG Scale",
                    info="Higher values = more adherence to your prompt, lower = more creative freedom."
                )
                negative_prompt = gr.Textbox(
                    label="Negative Prompt",
                    placeholder="Things to avoid in the image (e.g. blurry, low quality, watermark)",
                    lines=2,
                    info="Optional: Add things you don't want in the image."
                )
                generate_btn = gr.Button("Generate Comic", elem_id="generate-btn")
            
            with gr.Column():
                gr.Markdown("## Output & History")
                payload_display = gr.Textbox(
                    label="API Payload",
                    lines=6,
                    interactive=False,
                    info="Shows the exact payload sent to the Stable Diffusion API."
                )
                image = gr.Image(
                    label="Generated Image",
                    type="filepath"
                )
                history = gr.Dropdown(
                    label="Generation History",
                    choices=[],
                    interactive=True,
                    info="View your previous generations in this session."
                )
                
                export_btn = gr.Button("Export Session", elem_id="export-btn")
        
        gr.Markdown("""
        ---
        **Tips:**
        - Try different art styles and custom style combinations for variety.
        - Use negative prompts to filter out unwanted elements.
        - Export your session to save your work.
        - For best results, keep dimensions under 1536px.
        """)
        
        # Set up event handlers
        generate_btn.click(
            fn=generate_comic,
            inputs=[prompt, style_name, cfg_scale, negative_prompt, aspect_ratio_name, custom_dim, dim_type, custom_styles, gr.State(session_id)],
            outputs=[payload_display, image, history]
        )
        
        export_btn.click(
            fn=lambda: session_mgr.export_session(session_id),
            outputs=gr.File(label="Exported Session")
        )
    
    return demo 