import requests
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass

def call_llm(prompt: str, temperature: float = 0.7, timeout: int = 30) -> str:
    """
    Call the local LLM (Ollama) with the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Controls randomness (0.0 to 1.0)
        timeout: Request timeout in seconds
        
    Returns:
        str: The LLM's response text
        
    Raises:
        LLMError: If the LLM call fails
    """
    logger.info(f"Calling LLM with prompt length: {len(prompt)} chars")
    start_time = datetime.now()
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:12b",
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            },
            timeout=timeout
        )
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get("response", "")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"LLM call successful. Duration: {duration:.2f}s")
        logger.debug(f"LLM response length: {len(response_text)} chars")
        
        return response_text
        
    except requests.exceptions.Timeout:
        logger.error("LLM call timed out")
        raise LLMError("LLM request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM request failed: {str(e)}")
        raise LLMError(f"LLM request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in LLM call: {str(e)}")
        raise LLMError(f"Unexpected error: {str(e)}")

def call_llm_json(prompt: str, temperature: float = 0.7, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Call the LLM and parse its response as JSON.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Controls randomness (0.0 to 1.0)
        timeout: Request timeout in seconds
        
    Returns:
        Optional[Dict]: Parsed JSON response or None if parsing fails
    """
    logger.info("Calling LLM for JSON response")
    
    try:
        raw_response = call_llm(prompt, temperature, timeout)
        
        # Extract JSON block if extra text is present
        start = raw_response.find("[")
        end = raw_response.rfind("]") + 1
        
        if start == -1 or end == -1:
            logger.error("No JSON array found in LLM output")
            logger.debug(f"Raw response: {raw_response[:200]}...")
            return None
            
        json_str = raw_response[start:end]
        logger.debug(f"Extracted JSON string: {json_str[:200]}...")
        
        try:
            data = json.loads(json_str)
            logger.info(f"Successfully parsed JSON response with {len(data)} items")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            logger.debug(f"Problematic JSON string: {json_str[:200]}...")
            return None
            
    except LLMError as e:
        logger.error(f"LLM call failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in JSON parsing: {str(e)}")
        return None 