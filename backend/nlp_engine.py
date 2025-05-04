import logging
from typing import Optional
import ollama  # Added for official Ollama integration

logger = logging.getLogger('comic_insights.debug')

class NLPEngine:
    def __init__(self):
        # Placeholder for future NLP model initialization
        pass

    def generate_plot(self, prompt):
        """
        Placeholder for future plot generation
        Currently just returns a formatted version of the prompt
        """
        return f"Plot Summary:\n\n{prompt}\n\n(Note: This is a placeholder. Future versions will include AI-generated plot summaries.)"

    def generate_dialogue(self, prompt):
        """
        Placeholder for future dialogue generation
        """
        return f"Dialogue:\n\n(Note: This is a placeholder. Future versions will include AI-generated dialogue.)"

def generate_summary(prompt: str, context: Optional[str] = None) -> str:
    """Generate a story summary using Ollama Python client.
    
    Args:
        prompt (str): The user's story prompt.
        context (Optional[str]): Additional context for the prompt.
    
    Returns:
        str: The generated story summary.
    """
    logger.debug("Received story prompt: %s", prompt)
    
    # Build the system prompt
    system_prompt = """You are a professional comic book writer and creative storyteller.
Given the user's story prompt and any context, generate a vivid and concise summary for the first page or major scene of a comic or light novel.
The summary should be 1–3 paragraphs, rich in visual details, describing the scene, characters, and main action. Write so that the result can be easily visualized as a single comic page or illustration.

Your summary must:

- Clearly describe the setting, atmosphere, and mood  
- Mention the main character(s) and their appearance if available  
- Highlight key actions, emotions, or interactions in the scene  
- Be concise and focused—avoid filler or overly generic content  
- DO NOT write dialogue, break into panels, or include instructions—just a strong, visual narrative

Output only the story summary, no extra titles or commentary.

USER PROMPT: {prompt}

CONTEXT: {context}  # Only include this if context is provided

Generate the story summary now:"""
    
    full_prompt = system_prompt.format(prompt=prompt, context=context if context else "")
    logger.debug("Built full prompt: %s", full_prompt)
    
    try:
        response = ollama.generate(
            model='gemma3:12b',
            prompt=full_prompt
        )
        summary = response['response'].strip()
        logger.debug("Generated summary: %s", summary)
        return summary
    except Exception as e:
        logger.error("Error generating summary: %s", str(e))
        raise 