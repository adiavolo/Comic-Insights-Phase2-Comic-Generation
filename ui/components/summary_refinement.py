"""Summary refinement component for Comic Insights.

This module provides the UI and logic for interactive summary refinement,
supporting both manual edits and instruction-based refinement.
"""

import gradio as gr
from typing import Tuple, Optional
from dataclasses import dataclass
from ..utils.logging_utils import ComponentLogger
from ..utils.status_tracker import track_status
from backend import nlp_engine
from core.prompt.summary_refinement import (
    INITIAL_SUMMARY_PROMPT,
    LIGHT_CORRECTION_PROMPT,
    INSTRUCTION_REFINEMENT_PROMPT
)

logger = ComponentLogger(__name__)

@dataclass
class SummaryRefinementConfig:
    """Configuration for Summary Refinement component
    
    Attributes:
        summary_lines (int): Number of lines in the summary editor
        instruction_placeholder (str): Default text shown in instruction field
        instruction_info (str): Help text shown below instruction field
    """
    summary_lines: int = 10
    instruction_placeholder: str = "Enter refinement instruction (e.g., 'make it darker', 'add mystery')..."
    instruction_info: str = "Use natural language to guide the refinement process."

class SummaryRefinement:
    """Summary refinement component implementation
    
    This class manages the UI components and logic for interactive summary refinement,
    supporting both manual edits and instruction-based refinement.
    """
    
    def __init__(self, config: SummaryRefinementConfig = None):
        """Initialize Summary Refinement with optional custom configuration
        
        Args:
            config (SummaryRefinementConfig, optional): Custom configuration for the component.
                If not provided, uses default configuration.
        """
        self.config = config or SummaryRefinementConfig()
        self.logger = logger
        self.components = None
        self._last_llm_output = None
        self._is_final = False
        self._skip_next_change = False
    
    @track_status("SummaryRefinement")
    def create(self) -> Tuple[gr.Textbox, gr.Textbox, gr.Button, gr.Button, gr.Markdown, gr.Button]:
        """Create and return the Summary Refinement components
        
        Creates a complete UI for summary refinement, including:
        - Summary editor
        - Instruction input
        - Refinement button
        - Final confirmation button
        - Status message
        - Proceed button
        
        Returns:
            Tuple[gr.Textbox, gr.Textbox, gr.Button, gr.Button, gr.Markdown, gr.Button]: Refinement components
                - summary_editor: Text input for summary editing
                - instruction_input: Text input for refinement instructions
                - refine_btn: Button to apply instruction-based refinement
                - confirm_btn: Button to confirm final draft
                - status_message: Markdown element for status messages
                - proceed_btn: Button to proceed to character management
        """
        try:
            with gr.Column(elem_id="summary-refinement-container"):
                # --- Section: Summary Refinement Heading ---
                gr.Markdown(
                    "## ✍️ Summary Refinement",
                    elem_id="summary-refinement-heading"
                )
                gr.Markdown(
                    "<div style='margin-bottom: 18px; color: #555;'>"
                    "Edit your story summary below, or use an instruction for creative refinement."
                    "</div>",
                    elem_id="summary-refinement-desc"
                )

                # --- Group: Summary Editor ---
                with gr.Group(elem_id="summary-editor-group"):
                    gr.Markdown("**Story Summary**", elem_id="summary-editor-label")
                    summary_editor = gr.Textbox(
                        label="",
                        lines=self.config.summary_lines,
                        interactive=True,
                        elem_id="summary-editor",
                        show_label=False,
                        placeholder="Enter your story summary here..."
                    )
                    # Add word count display
                    gr.Markdown(
                        "<div id='word-count' style='text-align: right; color: #666; font-size: 0.9em;'>"
                        "Word count: <span id='word-count-value'>0</span>"
                        "</div>"
                    )

                # --- Group: Instruction Input ---
                with gr.Group(elem_id="instruction-group"):
                    gr.Markdown("**Refinement Instruction**", elem_id="instruction-label")
                    instruction_input = gr.Textbox(
                        label="",
                        placeholder=self.config.instruction_placeholder,
                        info=self.config.instruction_info,
                        elem_id="instruction-input",
                        show_label=False
                    )

                # --- Control Buttons Row ---
                with gr.Row(elem_id="control-buttons-row"):
                    refine_btn = gr.Button(
                        "Apply Refinement",
                        interactive=True,
                        variant="secondary",
                        elem_id="refine-btn"
                    )
                    confirm_btn = gr.Button(
                        "Confirm Final Draft",
                        interactive=True,
                        variant="primary",
                        elem_id="confirm-btn"
                    )

                # --- Status Message ---
                status_message = gr.Markdown(
                    "",
                    visible=False,
                    elem_id="status-message"
                )

                # --- Proceed Button (hidden by default, prominent when shown) ---
                proceed_btn = gr.Button(
                    "Proceed to character management",
                    visible=False,
                    variant="primary",
                    elem_id="proceed-btn"
                )

            self.components = (summary_editor, instruction_input, refine_btn, confirm_btn, status_message, proceed_btn)
            self.logger.info("Successfully created summary refinement components")
            return self.components
            
        except Exception as e:
            self.logger.error(f"Failed to create summary refinement components: {str(e)}")
            raise
    
    def attach_handlers(self):
        """Attach event handlers to summary refinement components
        
        Sets up the event handling for:
        - Manual edit detection and correction
        - Instruction-based refinement
        - Final draft confirmation
        
        Raises:
            RuntimeError: If called before components are created
        """
        if not self.components:
            raise RuntimeError("Components not created. Call create() first.")
        
        summary_editor, instruction_input, refine_btn, confirm_btn, status_message, proceed_btn = self.components
        
        # Handle instruction-based refinement
        refine_btn.click(
            fn=self._handle_instruction_refinement,
            inputs=[summary_editor, instruction_input],
            outputs=[summary_editor]
        )
        
        # Handle final confirmation (now clears and disables instruction input)
        confirm_btn.click(
            fn=self._handle_final_confirmation,
            inputs=[summary_editor, instruction_input],
            outputs=[summary_editor, instruction_input, status_message, refine_btn, confirm_btn, proceed_btn]
        )
        
        logger.debug("Summary refinement handlers attached.")
    
    def _handle_instruction_refinement(self, current_summary: str, instruction: str) -> str:
        """Handle instruction-based refinement
        
        Args:
            current_summary (str): The current state of the summary
            instruction (str): The refinement instruction
            
        Returns:
            str: The refined summary
        """
        if self._is_final:
            return current_summary
            
        refined = nlp_engine.process_prompt(
            INSTRUCTION_REFINEMENT_PROMPT.format(
                instruction=instruction,
                summary=current_summary
            )
        )
        self._last_llm_output = refined
        return refined
    
    def _handle_final_confirmation(self, current_summary: str, instruction: str):
        """Handle final draft confirmation
        
        Args:
            current_summary (str): The current state of the summary
            instruction (str): The refinement instruction (ignored)
        
        Returns:
            tuple: (corrected_summary, cleared_and_disabled_instruction_input, status_message, hide_refine_btn, hide_confirm_btn, show_proceed_btn)
        """
        self._is_final = True
        corrected = nlp_engine.process_prompt(
            LIGHT_CORRECTION_PROMPT.format(summary=current_summary)
        )
        self._last_llm_output = corrected
        
        # Enhanced status message with animation and icon
        status = (
            "<div style='"
            "color: #21c521; "
            "font-size: 1.5em; "
            "font-weight: bold; "
            "margin: 16px 0; "
            "padding: 16px; "
            "text-align: center; "
            "background: rgba(33, 197, 33, 0.1); "
            "border-radius: 8px; "
            "border: 1px solid rgba(33, 197, 33, 0.2); "
            "animation: fadeIn 0.5s ease; "
            "'>"
            "✓ Final story outline confirmed!"
            "</div>"
        )
        
        return (
            corrected,
            gr.update(value="", interactive=False),
            gr.update(value=status, visible=True),
            gr.update(interactive=False, visible=False),  # Hide/disable Apply Refinement
            gr.update(interactive=False, visible=False),  # Hide/disable Confirm Final Draft
            gr.update(visible=True, interactive=True)     # Show Proceed button
        ) 