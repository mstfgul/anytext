"""
Core text generation functionality.
"""
from typing import Dict, List, Optional, Any
import json

from api.openai_client import call_openai_api, parse_json_response
from config.language_data import LANGUAGE_MAP

def generate_text(
    language: str,
    level: str,
    word_count: int,
    topic: str,
    text_type: str = "General",
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Optional[str]:
    """
    Generate creative text for language learners.
    
    Args:
        language: Target language
        level: Language proficiency level
        word_count: Target word count
        topic: Text topic
        text_type: Type of text (General, Story, etc.)
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        Generated text or None if generation failed
    """
    # Convert language code to English name if needed
    lang_english = LANGUAGE_MAP.get(language, language)
    
    # Text type prompt addition
    text_type_prompt = ""
    if text_type != "General":
        text_type_mapping = {
            "Story": "a creative story",
            "Dialogue": "a dialogue between two or more people",
            "Letter": "a letter",
            "Article": "an article",
            "News": "a news article",
            "Informative": "an informative text"
        }
        text_type_prompt = f" Format the text as {text_type_mapping.get(text_type, '')}."
    
    # Text generation
    prompt = f"""Generate a creative and educational text in {lang_english} language on the topic: "{topic}".
    The text should be at {level} language proficiency level.
    The text should be approximately {word_count} words long.
    Make sure the vocabulary and grammar complexity match the specified language level.{text_type_prompt}
    Only provide the generated text, without any additional explanations or notes."""
    
    return call_openai_api(prompt, temperature, top_p, max_retries)

def get_topic_suggestion(
    language: str, 
    level: str,
    temperature: float = 0.9,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Optional[str]:
    """
    Get a topic suggestion for text generation.
    
    Args:
        language: Target language
        level: Language proficiency level
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        Topic suggestion or None if generation failed
    """
    lang_english = LANGUAGE_MAP.get(language, language)
    prompt = f"Suggest an interesting and educational topic for a {lang_english} text at {level} level. Return just the topic, no explanations."
    return call_openai_api(prompt, temperature, top_p, max_retries)

def generate_summary(
    text: str,
    language: str,
    level: str,
    temperature: float = 0.3,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Optional[str]:
    """
    Generate a summary of a text.
    
    Args:
        text: Source text to summarize
        language: Text language
        level: Language proficiency level
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        Generated summary or None if generation failed
    """
    lang_english = LANGUAGE_MAP.get(language, language)
    prompt = f"""Create a brief summary of the following {lang_english} text, suitable for {level} level language learners.
    The summary should be approximately 3-5 sentences and capture the main points.
    
    TEXT: {text[:2000]}"""  # Limit text to prevent token overflow
    
    return call_openai_api(prompt, temperature, top_p, max_retries)

def extract_key_words(
    text: str,
    language: str,
    level: str,
    count: int,
    temperature: float = 0.3,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Any:
    """
    Extract key vocabulary words from a text.
    
    Args:
        text: Source text to extract from
        language: Text language
        level: Language proficiency level
        count: Number of words to extract
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        List of dictionaries with word, definition, and example or raw text if parsing fails
    """
    lang_english = LANGUAGE_MAP.get(language, language)
    prompt = f"""From the following {lang_english} text, extract the {count} most important vocabulary words that would be helpful for {level} level language learners to study.
    For each word, provide:
    1. The word itself
    2. Its meaning/definition in {lang_english}
    3. An example sentence using the word (different from the original text)
    
    Format as a JSON list where each item has "word", "definition", and "example" keys.
    Make sure the JSON is properly formatted and valid.
    
    TEXT: {text[:1500]}"""  # Limit text to prevent token overflow
    
    result = call_openai_api(prompt, temperature, top_p, max_retries)
    if result:
        return parse_json_response(result)
    return None

def generate_comprehension_questions(
    text: str,
    language: str,
    level: str,
    count: int = 5,
    temperature: float = 0.3,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Any:
    """
    Generate comprehension questions for a text.
    
    Args:
        text: Source text for questions
        language: Text language
        level: Language proficiency level
        count: Number of questions to generate
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        Dictionary with list of questions and answers or raw text if parsing fails
    """
    lang_english = LANGUAGE_MAP.get(language, language)
    prompt = f"""Based on the following {lang_english} text, create {count} comprehension questions suitable for {level} level language learners.
    For each question:
    1. Write the question
    2. Provide the correct answer
    
    Format as a JSON object with "questions" as a list, where each item has "question" and "answer" keys.
    Make sure the JSON is properly formatted and valid.
    
    TEXT: {text[:1500]}"""  # Limit text to prevent token overflow
    
    result = call_openai_api(prompt, temperature, top_p, max_retries)
    if result:
        return parse_json_response(result)
    return None

def generate_language_exercises(
    text: str,
    language: str,
    level: str,
    count: int = 3,
    temperature: float = 0.4,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Any:
    """
    Generate language exercises based on a text.
    
    Args:
        text: Source text for exercises
        language: Text language
        level: Language proficiency level
        count: Number of exercises to generate
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        Dictionary with list of exercises or raw text if parsing fails
    """
    lang_english = LANGUAGE_MAP.get(language, language)
    prompt = f"""Based on the following {lang_english} text, create {count} language exercises suitable for {level} level learners.
    Create a mix of:
    - Fill-in-the-blank sentences
    - Grammar correction exercises
    - Word formation exercises
    
    For each exercise:
    1. Provide instructions
    2. The exercise content
    3. The correct answer/solution
    
    Format as a JSON object with "exercises" as a list, where each item has "instructions", "content", and "solution" keys.
    Make sure the JSON is properly formatted and valid.
    
    TEXT: {text[:1500]}"""  # Limit text to prevent token overflow
    
    result = call_openai_api(prompt, temperature, top_p, max_retries)
    if result:
        return parse_json_response(result)
    return None

def generate_translation(
    text: str,
    source_language: str,
    target_language: str,
    level: str,
    temperature: float = 0.3,
    top_p: float = 0.9,
    max_retries: int = 3
) -> Any:
    """
    Generate a line-by-line translation of a text.
    
    Args:
        text: Source text to translate
        source_language: Source language
        target_language: Target language
        level: Language proficiency level
        temperature: API temperature parameter
        top_p: API top_p parameter
        max_retries: Maximum API retry attempts
        
    Returns:
        List of dictionaries with original and translation or raw text if parsing fails
    """
    source_lang_english = LANGUAGE_MAP.get(source_language, source_language)
    target_lang_english = LANGUAGE_MAP.get(target_language, target_language)
    
    prompt = f"""Translate the following {source_lang_english} text into {target_lang_english}, line by line.
    Provide a translation that is appropriate for {level} level language learners.
    For each line, give both the original text and its translation.
    
    Format as a JSON array where each item has "original" and "translation" keys.
    Make sure the JSON is properly formatted and valid.
    
    TEXT:
    {text[:2000]}"""  # Limit text to prevent token overflow
    
    result = call_openai_api(prompt, temperature, top_p, max_retries)
    if result:
        return parse_json_response(result)
    return None