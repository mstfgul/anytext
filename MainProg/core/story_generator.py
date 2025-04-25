"""
Interactive story generation functionality.
"""
from typing import Dict, List, Optional, Any, Union

from api.openai_client import call_openai_api, parse_json_response
from config.language_data import LANGUAGE_MAP

def generate_story_part(
    language: str,
    level: str,
    topic: str,
    part_number: int,
    previous_text: str = "",
    choice_made: str = "",
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Generate a part of an interactive story with two choices for continuation.
    
    Args:
        language: Target language
        level: Language proficiency level
        topic: Story topic or title
        part_number: Which part of the story this is
        previous_text: The previous parts of the story (for context)
        choice_made: The choice the user made to continue the story
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        Dictionary with story text and choices or None if generation failed
    """
    lang_english = LANGUAGE_MAP.get(language, language)
    
    # First part of the story
    if part_number == 1:
        prompt = f"""Generate the beginning of an interactive story in {lang_english} at {level} level with the title/topic: "{topic}".
        
        The story should be appropriate for language learners at {level} level.
        Write approximately 200-250 words for this first part.
        
        At the end of this part, provide TWO different choices for how the story could continue.
        
        Format your response as a JSON object with these fields:
        - "story_text": The main text of this part of the story
        - "choice_1": A brief description of the first choice (about 15-20 words)
        - "choice_2": A brief description of the second choice (about 15-20 words)
        
        Make sure the JSON is properly formatted and valid.
        """
    else:
        # Continuation based on previous choice
        prompt = f"""Continue the interactive story in {lang_english} at {level} level.
        
        Previous story parts:
        {previous_text}
        
        The reader chose: "{choice_made}"
        
        Continue the story based on this choice for approximately 200-250 words.
        
        At the end of this part, provide TWO different choices for how the story could continue.
        Unless this should be the final part (part {part_number}), in which case provide a satisfying ending with no choices.
        
        Format your response as a JSON object with these fields:
        - "story_text": The continuation of the story based on the choice made
        - "choice_1": A brief description of the first choice (about 15-20 words) or empty string if it's the final part
        - "choice_2": A brief description of the second choice (about 15-20 words) or empty string if it's the final part
        - "is_final": Boolean value (true/false) indicating if this is the final part of the story
        
        Make sure the JSON is properly formatted and valid.
        """
    
    result = call_openai_api(prompt, temperature, top_p, max_retries)
    if result:
        parsed_result = parse_json_response(result)
        if isinstance(parsed_result, dict):
            return parsed_result
    return None

class Story:
    """Class representing an interactive story."""
    
    def __init__(
        self,
        title: str,
        language: str,
        level: str
    ):
        """
        Initialize a new story.
        
        Args:
            title: Story title
            language: Story language
            level: Language proficiency level
        """
        self.title = title
        self.language = language
        self.level = level
        self.parts = {}  # Dict of story parts
        self.vocabulary = None
        self.translation = None
        self.translation_language = None
    
    def add_part(
        self,
        part_number: int,
        text: str,
        choice_1: str = "",
        choice_2: str = "",
        is_final: bool = False,
        choice_made: str = ""
    ) -> Dict[str, Union[str, bool]]:
        """
        Add a new part to the story.
        
        Args:
            part_number: Part number
            text: Part text
            choice_1: First choice
            choice_2: Second choice
            is_final: Whether this is the final part
            choice_made: Choice that led to this part
            
        Returns:
            The part data dictionary
        """
        part_key = f"part_{part_number}"
        part_data = {
            'text': text,
            'choice_1': choice_1,
            'choice_2': choice_2,
            'is_final': is_final
        }
        
        if choice_made:
            part_data['choice_made'] = choice_made
            
        self.parts[part_key] = part_data
        return part_data
    
    def get_current_text(self, up_to_part: Optional[int] = None) -> str:
        """
        Get the complete story text up to a specific part.
        
        Args:
            up_to_part: Part number to get text up to (or all parts if None)
            
        Returns:
            Concatenated story text
        """
        full_text = ""
        part_numbers = sorted([int(key.split('_')[1]) for key in self.parts.keys()])
        
        for part_num in part_numbers:
            if up_to_part is not None and part_num > up_to_part:
                break
                
            part_key = f"part_{part_num}"
            full_text += self.parts[part_key]['text'] + "\n\n"
            
        return full_text
    
    def get_latest_part(self) -> Dict[str, Any]:
        """
        Get the latest part of the story.
        
        Returns:
            The latest part data or empty dict if no parts
        """
        if not self.parts:
            return {}
            
        part_numbers = sorted([int(key.split('_')[1]) for key in self.parts.keys()])
        latest_part_num = part_numbers[-1]
        part_key = f"part_{latest_part_num}"
        
        return {
            'part_number': latest_part_num,
            'data': self.parts[part_key]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert story to dictionary for storage.
        
        Returns:
            Dictionary representation of the story
        """
        return {
            'title': self.title,
            'language': self.language,
            'level': self.level,
            'parts': self.parts,
            'vocabulary': self.vocabulary,
            'translation': self.translation,
            'translation_language': self.translation_language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Story':
        """
        Create a Story instance from a dictionary.
        
        Args:
            data: Dictionary with story data
            
        Returns:
            Story instance
        """
        story = cls(
            title=data['title'],
            language=data['language'],
            level=data['level']
        )
        
        story.parts = data['parts']
        story.vocabulary = data.get('vocabulary')
        story.translation = data.get('translation')
        story.translation_language = data.get('translation_language')
        
        return story