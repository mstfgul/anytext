"""
Data models for text generation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import datetime

@dataclass
class KeyWord:
    """Model for key vocabulary word."""
    word: str
    definition: str
    example: str

@dataclass
class Question:
    """Model for comprehension question."""
    question: str
    answer: str

@dataclass
class Exercise:
    """Model for language exercise."""
    instructions: str
    content: str
    solution: str

@dataclass
class Translation:
    """Model for translation line."""
    original: str
    translation: str

@dataclass
class GeneratedText:
    """Model for a complete generated text with all associated content."""
    topic: str
    text: str
    language: str
    level: str
    text_type: str = "General"
    summary: Optional[str] = None
    key_words: List[Any] = field(default_factory=list)
    questions: List[Any] = field(default_factory=list)
    exercises: List[Any] = field(default_factory=list)
    translation: List[Any] = field(default_factory=list)
    translation_language: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    word_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for storage.
        
        Returns:
            Dictionary representation
        """
        return {
            "topic": self.topic,
            "text": self.text,
            "language": self.language,
            "level": self.level,
            "text_type": self.text_type,
            "summary": self.summary,
            "key_words": self._convert_to_dict_list(self.key_words) if self.key_words else None,
            "questions": self._convert_to_dict_list(self.questions) if self.questions else None,
            "exercises": self._convert_to_dict_list(self.exercises) if self.exercises else None,
            "translation": self._convert_to_dict_list(self.translation) if self.translation else None,
            "translation_language": self.translation_language,
            "timestamp": self.timestamp,
            "word_count": self.word_count
        }
    
    def _convert_to_dict_list(self, items: List[Any]) -> List[Dict[str, Any]]:
        """
        Convert a list of items to a list of dictionaries.
        
        This handles both dataclass instances and dictionaries.
        
        Args:
            items: List of items to convert
            
        Returns:
            List of dictionaries
        """
        result = []
        for item in items:
            if hasattr(item, '__dict__'):
                # For dataclass instances or objects with __dict__
                result.append(vars(item))
            elif isinstance(item, dict):
                # For dictionary items
                result.append(item)
            else:
                # For other types, try to convert to dictionary or use string representation
                try:
                    result.append(dict(item))
                except (TypeError, ValueError):
                    result.append({"value": str(item)})
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedText':
        """
        Create instance from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            GeneratedText instance
        """
        instance = cls(
            topic=data["topic"],
            text=data["text"],
            language=data["language"],
            level=data["level"]
        )
        
        # Set optional fields
        instance.text_type = data.get("text_type", "General")
        instance.summary = data.get("summary")
        instance.translation_language = data.get("translation_language")
        instance.timestamp = data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        instance.word_count = data.get("word_count", 0)
        
        # Convert list data
        if data.get("key_words"):
            if isinstance(data["key_words"], list):
                instance.key_words = [KeyWord(**kw) for kw in data["key_words"]]
            
        if data.get("questions"):
            if isinstance(data["questions"], list):
                instance.questions = [Question(**q) for q in data["questions"]]
            elif isinstance(data["questions"], dict) and "questions" in data["questions"]:
                instance.questions = [Question(**q) for q in data["questions"]["questions"]]
        
        if data.get("exercises"):
            if isinstance(data["exercises"], list):
                instance.exercises = [Exercise(**ex) for ex in data["exercises"]]
            elif isinstance(data["exercises"], dict) and "exercises" in data["exercises"]:
                instance.exercises = [Exercise(**ex) for ex in data["exercises"]["exercises"]]
        
        if data.get("translation"):
            if isinstance(data["translation"], list):
                instance.translation = [Translation(**t) for t in data["translation"]]
        
        return instance