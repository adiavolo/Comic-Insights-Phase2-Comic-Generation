"""Prompts for interactive summary refinement.

This module contains the prompts used for:
1. Initial story summary generation
2. Light correction of manual edits
3. Instruction-based refinement
"""

INITIAL_SUMMARY_PROMPT = """
Generate a vivid, engaging story summary (1-3 paragraphs) based on the following prompt:
{prompt}

Focus on:
- Rich, descriptive language
- Clear narrative flow
- Engaging character and setting details
- Natural pacing and structure
"""

LIGHT_CORRECTION_PROMPT = """
Please correct only grammar, sentence flow, and clarity in the following text.
Do not change the meaning, structure, or add/remove content.
Try to retain the length and level of detail of the original summary as much as possible.
Return ONLY the corrected summary. Do not include explanations or commentary:

{summary}
"""

INSTRUCTION_REFINEMENT_PROMPT = """
Revise the following story summary according to this instruction: "{instruction}".
Be creative as needed while maintaining the core narrative.
Try to retain the length and level of detail of the original summary as much as possible.
Return ONLY the revised summary. Do not include explanations or commentary:

{summary}
""" 