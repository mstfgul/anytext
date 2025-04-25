"""
Main application entry point for the Flask-based web interface.
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import datetime  # Added missing import
from dotenv import load_dotenv

# Load our application modules
from config.settings import DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_FONT_SIZE, DEFAULT_WORD_COUNT
from config.language_data import LANGUAGE_MAP, DIFFICULTY_WORDS_COUNT, TEXT_TYPES, PROFICIENCY_LEVELS
from core.text_generator import (
    generate_text, 
    get_topic_suggestion, 
    generate_summary, 
    extract_key_words,
    generate_comprehension_questions,
    generate_language_exercises,
    generate_translation
)
from core.story_generator import generate_story_part, Story
from storage.session_manager import SessionManager
from models.text import GeneratedText

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            static_folder='web/static',
            template_folder='web/templates')

# Configure Flask app
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize session manager
session_manager = SessionManager()

# Routes
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html', 
                          languages=LANGUAGE_MAP.keys(),
                          levels=PROFICIENCY_LEVELS,
                          text_types=TEXT_TYPES)

@app.route('/text-generator')
def text_generator():
    """Render the text generator page."""
    return render_template('text_generator.html',
                          languages=LANGUAGE_MAP.keys(),
                          levels=PROFICIENCY_LEVELS,
                          text_types=TEXT_TYPES,
                          word_counts=[500, 750, 1000])

@app.route('/interactive-story')
def interactive_story():
    """Render the interactive story page."""
    return render_template('interactive_story.html',
                          languages=LANGUAGE_MAP.keys(),
                          levels=PROFICIENCY_LEVELS)

@app.route('/history')
def history():
    """Render the history page."""
    return render_template('history.html',
                          history=session_manager.get('history', []),
                          stories=session_manager.list_stories())

# API Routes for AJAX calls

@app.route('/api/generate-text', methods=['POST'])
def api_generate_text():
    """API endpoint to generate text."""
    try:
        data = request.json
        
        language = data.get('language', 'English')
        level = data.get('level', 'B1-B2')
        word_count = int(data.get('word_count', DEFAULT_WORD_COUNT))
        topic = data.get('topic')
        text_type = data.get('text_type', 'General')
        temperature = float(data.get('temperature', DEFAULT_TEMPERATURE))
        top_p = float(data.get('top_p', DEFAULT_TOP_P))
        
        # If no topic provided, generate one
        if not topic:
            topic = get_topic_suggestion(language, level, temperature, top_p)
            if not topic:
                return jsonify({"error": "Failed to generate topic"}), 500
        
        # Generate the text
        generated_text = generate_text(
            language=language,
            level=level,
            word_count=word_count,
            topic=topic,
            text_type=text_type,
            temperature=temperature,
            top_p=top_p
        )
        
        if not generated_text:
            return jsonify({"error": "Failed to generate text"}), 500
        
        # Create a GeneratedText object
        text_obj = GeneratedText(
            topic=topic,
            text=generated_text,
            language=language,
            level=level,
            text_type=text_type,
            word_count=word_count
        )
        
        # Generate additional content if requested
        include_summary = data.get('include_summary', False)
        include_key_words = data.get('include_key_words', False)
        include_questions = data.get('include_questions', False)
        include_exercises = data.get('include_exercises', False)
        include_translation = data.get('include_translation', False)
        
        if include_summary:
            summary = generate_summary(generated_text, language, level)
            if summary:
                text_obj.summary = summary
        
        if include_key_words:
            word_count = DIFFICULTY_WORDS_COUNT.get(level, 5)
            key_words = extract_key_words(generated_text, language, level, word_count)
            if key_words:
                text_obj.key_words = key_words
        
        if include_questions:
            questions = generate_comprehension_questions(generated_text, language, level)
            if questions:
                text_obj.questions = questions
        
        if include_exercises:
            exercises = generate_language_exercises(generated_text, language, level)
            if exercises:
                text_obj.exercises = exercises
        
        if include_translation:
            translation_language = data.get('translation_language', 'English')
            if translation_language != language:
                translation = generate_translation(
                    generated_text, 
                    language, 
                    translation_language, 
                    level
                )
                if translation:
                    text_obj.translation = translation
                    text_obj.translation_language = translation_language
        
        # Save to history
        if data.get('save_history', True):
            session_manager.add_to_history(text_obj.to_dict())
        
        # Return the results
        return jsonify({
            "success": True,
            "text": text_obj.to_dict()
        })
        
    except Exception as e:
        import traceback
        print(f"Error in api_generate_text: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-story-part', methods=['POST'])
def api_generate_story_part():
    """API endpoint to generate a story part."""
    try:
        data = request.json
        
        language = data.get('language', 'English')
        level = data.get('level', 'B1-B2')
        topic = data.get('topic', '')
        part_number = int(data.get('part_number', 1))
        previous_text = data.get('previous_text', '')
        choice_made = data.get('choice_made', '')
        temperature = float(data.get('temperature', DEFAULT_TEMPERATURE))
        top_p = float(data.get('top_p', DEFAULT_TOP_P))
        
        # Generate the story part
        story_part = generate_story_part(
            language=language,
            level=level,
            topic=topic,
            part_number=part_number,
            previous_text=previous_text,
            choice_made=choice_made,
            temperature=temperature,
            top_p=top_p
        )
        
        if not story_part:
            return jsonify({"error": "Failed to generate story part"}), 500
        
        # If this is the first part or we don't have the story yet, create it
        story_id = data.get('story_id', topic)
        story = session_manager.get_story(story_id)
        
        if not story:
            story = {
                'title': story_id,
                'language': language,
                'level': level,
                'parts': {},
                'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Add the new part
        part_key = f"part_{part_number}"
        story['parts'][part_key] = {
            'text': story_part.get('story_text', ''),
            'choice_1': story_part.get('choice_1', ''),
            'choice_2': story_part.get('choice_2', ''),
            'is_final': story_part.get('is_final', False)
        }
        
        if choice_made:
            story['parts'][part_key]['choice_made'] = choice_made
        
        # Update last updated timestamp
        story['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save the story
        session_manager.save_story(story_id, story)
        
        # Return the results
        return jsonify({
            "success": True,
            "story_part": story_part,
            "story_id": story_id
        })
        
    except Exception as e:
        import traceback
        print(f"Error in api_generate_story_part: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-story', methods=['GET'])
def api_get_story():
    """API endpoint to get a story."""
    try:
        story_id = request.args.get('story_id')
        if not story_id:
            return jsonify({"error": "Story ID is required"}), 400
        
        story = session_manager.get_story(story_id)
        if not story:
            return jsonify({"error": "Story not found"}), 404
        
        return jsonify({
            "success": True,
            "story": story
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/list-stories', methods=['GET'])
def api_list_stories():
    """API endpoint to list all stories."""
    try:
        stories = session_manager.list_stories()
        return jsonify({
            "success": True,
            "stories": stories
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-story', methods=['POST'])
def api_delete_story():
    """API endpoint to delete a story."""
    try:
        data = request.json
        story_id = data.get('story_id')
        
        if not story_id:
            return jsonify({"error": "Story ID is required"}), 400
        
        success = session_manager.delete_story(story_id)
        if not success:
            return jsonify({"error": "Failed to delete story"}), 500
        
        return jsonify({
            "success": True,
            "message": f"Story '{story_id}' deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-history', methods=['GET'])
def api_get_history():
    """API endpoint to get text generation history."""
    try:
        history = session_manager.get('history', [])
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-history', methods=['POST'])
def api_clear_history():
    """API endpoint to clear text generation history."""
    try:
        session_manager.clear_history()
        return jsonify({
            "success": True,
            "message": "History cleared successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-topic', methods=['POST'])
def api_generate_topic():
    """API endpoint to generate a topic suggestion."""
    try:
        data = request.json
        language = data.get('language', 'English')
        level = data.get('level', 'B1-B2')
        
        topic = get_topic_suggestion(language, level)
        if not topic:
            return jsonify({"error": "Failed to generate topic"}), 500
        
        return jsonify({
            "success": True,
            "topic": topic
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-summary', methods=['POST'])
def api_generate_summary():
    """API endpoint to generate a summary."""
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'English')
        level = data.get('level', 'B1-B2')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        summary = generate_summary(text, language, level)
        if not summary:
            return jsonify({"error": "Failed to generate summary"}), 500
        
        return jsonify({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional API endpoints for other functionalities would follow the same pattern

if __name__ == '__main__':
    app.run(debug=True)