"""
OpenAI API client wrapper.
"""
import time
import openai
from typing import Optional, Dict, Any, List

from config.settings import OPENAI_API_KEY, DEFAULT_MODEL, API_MAX_RETRIES, API_TIMEOUT

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def call_openai_api(
    prompt: str, 
    temperature: float = 0.7, 
    top_p: float = 0.9, 
    max_retries: int = API_MAX_RETRIES,
    model: str = DEFAULT_MODEL
) -> Optional[str]:
    """
    Call OpenAI API with retry logic.
    
    Args:
        prompt: The prompt to send to the API
        temperature: Controls randomness (0-1)
        top_p: Controls diversity (0-1)
        max_retries: Maximum number of retry attempts
        model: The model name to use
        
    Returns:
        The API response text or None if the request failed
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative text generator for language learners."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                top_p=top_p,
                timeout=API_TIMEOUT
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API error: {e}")  # Better error logging
            retry_count += 1
            if retry_count >= max_retries:
                return None
            time.sleep(1)  # Brief waiting period

def parse_json_response(response: str) -> Any:
    """
    Parse a JSON response from the API, handling common formatting issues.
    
    Args:
        response: The response string from the API
        
    Returns:
        Parsed JSON object or the original string if parsing fails
    """
    import json
    
    try:
        # Clean up the response to handle common formatting issues
        cleaned_result = response.strip()
        
        # Remove markdown code block markers if present
        if cleaned_result.startswith("```json"):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.endswith("```"):
            cleaned_result = cleaned_result[:-3]
            
        cleaned_result = cleaned_result.strip()
        
        return json.loads(cleaned_result)
    except json.JSONDecodeError:
        # If parsing fails, return the raw text
        return response