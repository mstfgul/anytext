"""
Session state management for the application.
Works with different frontends (Streamlit, web app).
"""
import json
import datetime
from typing import Dict, List, Any, Optional, Union

class SessionManager:
    """Manages application session data."""
    
    def __init__(self, storage_type: str = "memory"):
        """
        Initialize session manager.
        
        Args:
            storage_type: Type of storage backend ("memory", "file", etc.)
        """
        self.storage_type = storage_type
        self.data = {
            'history': [],
            'current_text': "",
            'current_topic': "",
            'current_summary': "",
            'current_key_words': "",
            'current_questions': "",
            'current_exercises': "",
            'current_translation': "",
            'stories': {},
            'current_story_id': None,
            'current_story_part': 1,
            'current_choices': []
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from session data.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            The stored value or default
        """
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in session data.
        
        Args:
            key: Data key
            value: Value to store
        """
        self.data[key] = value
    
    def add_to_history(self, item: Dict[str, Any]) -> None:
        """
        Add an item to text generation history.
        
        Args:
            item: History item data
        """
        if 'timestamp' not in item:
            item['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        history = self.data.get('history', [])
        history.append(item)
        self.data['history'] = history
    
    def clear_history(self) -> None:
        """Clear text generation history."""
        self.data['history'] = []
    
    def save_story(self, story_id: str, story_data: Dict[str, Any]) -> None:
        """
        Save a story to storage.
        
        Args:
            story_id: Story identifier
            story_data: Story data dictionary
        """
        stories = self.data.get('stories', {})
        stories[story_id] = story_data
        self.data['stories'] = stories
    
    def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a story from storage.
        
        Args:
            story_id: Story identifier
            
        Returns:
            Story data or None if not found
        """
        stories = self.data.get('stories', {})
        return stories.get(story_id)
    
    def delete_story(self, story_id: str) -> bool:
        """
        Delete a story from storage.
        
        Args:
            story_id: Story identifier
            
        Returns:
            True if story was deleted, False otherwise
        """
        stories = self.data.get('stories', {})
        if story_id in stories:
            del stories[story_id]
            self.data['stories'] = stories
            return True
        return False
    
    def list_stories(self) -> List[Dict[str, Any]]:
        """
        List all stories with metadata.
        
        Returns:
            List of story metadata dictionaries
        """
        stories = self.data.get('stories', {})
        result = []
        
        for story_id, story_data in stories.items():
            parts_count = len(story_data.get('parts', {}))
            latest_part = max([int(k.split('_')[1]) for k in story_data.get('parts', {}).keys()]) if story_data.get('parts') else 0
            is_complete = latest_part > 0 and story_data.get('parts', {}).get(f'part_{latest_part}', {}).get('is_final', False)
            
            result.append({
                'id': story_id,
                'title': story_id,
                'language': story_data.get('language', ''),
                'level': story_data.get('level', ''),
                'parts_count': parts_count,
                'is_complete': is_complete,
                'last_updated': story_data.get('last_updated', '')
            })
            
        return result
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export all session data for backup or storage.
        
        Returns:
            Dictionary of all session data
        """
        return self.data
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """
        Import session data from backup or storage.
        
        Args:
            data: Session data dictionary
        """
        self.data = data
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save session data to a file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load session data from a file.
        
        Args:
            filepath: Path to load file from
            
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except Exception:
            return False