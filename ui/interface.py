import gradio as gr
import os
from datetime import datetime
from backend import img_api, nlp_engine, session_manager
from .prompt_manager import PromptManager
import logging

# Initialize backend components
img_generator = img_api.ImageAPI()
nlp = nlp_engine  # Use the singleton instance from backend/__init__.py
session_mgr = session_manager  # Use the singleton instance from backend/__init__.py

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

def create_plot_story_tab():
    """Create the Plot/Story Setup tab UI"""
    logger = logging.getLogger('comic_insights.debug')
    logger.debug("Initializing Plot/Story Setup tab UI.")
    
    from .components.story_tab import StoryTab
    from .components.summary_refinement import SummaryRefinement
    
    with gr.Tab("Plot/Story Setup"):
        gr.Markdown("""
        # Plot/Story Setup
        Enter your story details and scene descriptions here.
        """)
        
        # Initialize our components
        story_tab = StoryTab()
        story_prompt, generate_story_btn, story_output = story_tab.create()
        
        # Create the summary refinement section (only once)
        summary_refinement = SummaryRefinement()
        summary_editor, instruction_input, refine_btn, confirm_btn, status_message, proceed_btn = summary_refinement.create()
        
        # Notification output
        story_notify = gr.Markdown(visible=True)
        
        # Unique tips for Plot/Story Setup
        gr.Markdown("""
        ---
        **Tips:**
        - Start with a clear summary of your comic's plot or scene.
        - Include main characters and their motivations.
        - Mention the setting and any important background details.
        - Keep your description concise but vivid for best results.
        - Use the refinement tools to polish your story summary.
        """)
        logger.info("Plot/Story Setup tab UI initialized.")
        
        # Attach handlers
        story_tab.attach_handlers()
        summary_refinement.attach_handlers()
        
        # When the summary is generated, update both the output and the summary editor
        def update_summary_and_editor(user_input):
            summary, _ = story_tab._generate_initial_summary(user_input)
            summary_refinement._skip_next_change = True
            return summary, summary
        generate_story_btn.click(
            fn=update_summary_and_editor,
            inputs=[story_prompt],
            outputs=[story_output, summary_editor]
        )
        
    return story_prompt, generate_story_btn, story_output, summary_editor

def create_character_management_tab():
    """Create the Character Management tab UI"""
    logger = logging.getLogger('comic_insights.debug')
    logger.debug("Initializing Character Management tab UI.")
    with gr.Tab("Character Management"):
        gr.Markdown("""
        # Character Management
        Manage your comic characters and their appearances.
        """)
        add_character_btn = gr.Button(
            "Add New Character",
            interactive=False
        )
        character_list = gr.Markdown(
            """
            | Character Name | Description | Appearance |
            |---------------|-------------|------------|
            | Coming Soon   | Feature in development | - |
            """,
            label="Character List"
        )
        gr.Markdown("""
        You will be able to add character appearance details for prompt consistency.
        """)
        # Unique tips for Character Management
        gr.Markdown("""
        ---
        **Tips:**
        - Add each character with a unique name and role.
        - Describe their appearance, personality, and relationships.
        - Use consistent details for recurring characters.
        - Update the roster as your story evolves.
        """)
        logger.info("Character Management tab UI initialized.")
    return add_character_btn, character_list

def create_interface():
    """Create and return the Gradio interface"""
    logger = logging.getLogger('comic_insights.debug')
    status_logger = logging.getLogger('comic_insights.status')
    logger.debug("Creating new session for Comic Insights UI.")
    # Create a new session
    session_id = session_mgr.create_session()
    status_logger.info(f"Session created with ID: {session_id}")
    
    with gr.Blocks(title="Comic Insights") as demo:
        gr.Markdown("""
        # Comic Insights
        Welcome to Comic Insights! Generate unique comic pages with AI-powered art and text.
        """)
        logger.debug("Main Comic Insights UI loaded.")
        
        # Create tabs
        with gr.Tabs():
            # Tab 1: Plot/Story Setup
            story_prompt, generate_story_btn, story_output, summary_editor = create_plot_story_tab()
            logger.debug("Plot/Story Setup tab added to UI.")
            
            # Tab 2: Image Generation & Editing (current implementation)
            with gr.Tab("Image Generation & Editing"):
                logger.debug("Initializing Image Generation & Editing tab UI.")
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
                # Unique tips for Image Generation & Editing
                gr.Markdown("""
                ---
                **Tips:**
                - Try different art styles and custom style combinations for variety.
                - Use negative prompts to filter out unwanted elements.
                - Export your session to save your work.
                - For best results, keep dimensions under 1536px.
                """)
                logger.info("Image Generation & Editing tab UI initialized.")
            
            # Tab 3: Character Management
            add_character_btn, character_list = create_character_management_tab()
            logger.debug("Character Management tab added to UI.")
        
        # Set up event handlers for image generation tab
        logger.debug("Setting up event handlers for image generation tab.")
        generate_btn.click(
            fn=generate_comic,
            inputs=[prompt, style_name, cfg_scale, negative_prompt, aspect_ratio_name, custom_dim, dim_type, custom_styles, gr.State(session_id)],
            outputs=[payload_display, image, history]
        )
        
        export_btn.click(
            fn=lambda: session_mgr.export_session(session_id),
            outputs=gr.File(label="Exported Session")
        )
        logger.info("Comic Insights UI fully initialized and ready.")
    
    return demo 