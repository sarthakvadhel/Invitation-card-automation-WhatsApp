#!/usr/bin/env python3
"""
Invitation Card Web Application
Flask-based web app for sending invitation cards via WhatsApp
"""

import os
import re
import threading
from flask import Flask, render_template, request, jsonify, send_file
from googletrans import Translator
import signal
from contextlib import contextmanager
import io

app = Flask(__name__)

# Initialize Google Translator (reuse instance for efficiency)
translator = Translator()


class TimeoutException(Exception):
    """Exception raised when an operation times out"""
    pass


# Lock to ensure only one timeout is active at a time (for signal-based timeouts)
_timeout_lock = threading.Lock()


@contextmanager
def time_limit(seconds):
    """Context manager to limit execution time of a code block"""
    def signal_handler(signum, frame):
        raise TimeoutException("Operation timed out")
    
    # Set up the signal handler only on Unix-like systems
    if hasattr(signal, 'SIGALRM'):
        # Use lock to prevent concurrent timeouts (signal is process-wide)
        with _timeout_lock:
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
    else:
        # On Windows or systems without SIGALRM, just execute without timeout
        yield


# Translation mapping for English to Gujarati
ENGLISH_TO_GUJARATI = {
    # Special exception
    'vadhel': 'વઢેળ',
    
    # Common titles
    'bhai': 'ભાઈ',
    'ben': 'બેન',
    'shri': 'શ્રી',
    
    # Common surnames
    'patel': 'પટેલ',
    'desai': 'દેસાઈ',
    'shah': 'શાહ',
    'modi': 'મોદી',
    'joshi': 'જોશી',
    'dave': 'દવે',
    'mehta': 'મેહતા',
    'trivedi': 'ત્રિવેદી',
    'pandya': 'પંડ્યા',
    'sharma': 'શર્મા',
    'parikh': 'પારીખ',
    'vyas': 'વ્યાસ',
    'amin': 'અમીન',
    'thakkar': 'ઠક્કર',
    'solanki': 'સોલંકી',
    'raval': 'રાવલ',
    'bhatt': 'ભટ્ટ',
    'bhavsar': 'ભાવસાર',
    'choksi': 'ચોકસી',
    'dalal': 'દલાલ',
    'gandhi': 'ગાંધી',
    'kapadia': 'કપાડિયા',
    'mistry': 'મિસ્ત્રી',
    'panchal': 'પંચાલ',
    'rathod': 'રાઠોડ',
    'sanghvi': 'સંઘવી',
    'vora': 'વોરા',
    
    # Common first names (male)
    'ramesh': 'રમેશ',
    'mahesh': 'મહેશ',
    'suresh': 'સુરેશ',
    'mukesh': 'મુકેશ',
    'rajesh': 'રાજેશ',
    'paresh': 'પરેશ',
    'nilesh': 'નિલેશ',
    'hitesh': 'હિતેશ',
    'jignesh': 'જિગ્નેશ',
    'dipak': 'દિપક',
    'amit': 'અમિત',
    'vijay': 'વિજય',
    'ajay': 'અજય',
    'sanjay': 'સંજય',
    'jayesh': 'જયેશ',
    'manish': 'મનિષ',
    'ravi': 'રવિ',
    'prakash': 'પ્રકાશ',
    'ashok': 'અશોક',
    'vinod': 'વિનોદ',
    'anil': 'અનિલ',
    'kishore': 'કિશોર',
    'bharat': 'ભરત',
    'kiran': 'કિરણ',
    'yogesh': 'યોગેશ',
    'naresh': 'નરેશ',
    'dinesh': 'દિનેશ',
    'sandip': 'સંદીપ',
    'harish': 'હરીશ',
    'jagdish': 'જગદીશ',
    'girish': 'ગિરીશ',
    'sarthak': 'સાર્થક',
    'vasudha': 'વસુધા',
    'vanrajbhai': 'વનરાજભાઈ',
    
    # Common first names (female)
    'kalpana': 'કલ્પના',
    'anita': 'અનિતા',
    'meera': 'મીરા',
    'geeta': 'ગીતા',
    'sita': 'સીતા',
    'nisha': 'નિશા',
    'priya': 'પ્રિયા',
    'kavita': 'કવિતા',
    'nita': 'નીતા',
    'rita': 'રીતા',
    'mita': 'મીતા',
    'lata': 'લતા',
    'asha': 'આશા',
    'usha': 'ઉષા',
    'rekha': 'રેખા',
    'shobha': 'શોભા',
    'manjula': 'મંજુલા',
    'sarita': 'સરિતા',
    'sunita': 'સુનિતા',
    'kanta': 'કાંતા',
    'pramila': 'પ્રમિલા',
    'sharda': 'શારદા',
    'kokila': 'કોકિલા',
    'hansa': 'હંસા',
    'leela': 'લીલા',
    'maya': 'માયા',
    'neeta': 'નીતા',
    'vaishali': 'વૈશાલી',
    'bharti': 'ભારતી',
    'dipti': 'દીપ્તી',
}

# WhatsApp sender configurations
WHATSAPP_SENDERS = {
    'sarthak': {
        'name': 'Sarthak',
    },
    'vanrajbhai': {
        'name': 'Vanrajbhai',
    },
    'vasudha': {
        'name': 'Vasudha',
    }
}


def transliterate_to_gujarati(english_text):
    """
    Transliterate English text to Gujarati script using Google Translate.
    Special exception: "Vadhel" is always translated as "વઢેળ"
    Falls back to dictionary-based translation if Google Translate fails or times out.
    """
    if not english_text:
        return ""
    
    # Check if already in Gujarati (contains Gujarati Unicode characters)
    if any(ord(c) >= 0x0A80 and ord(c) <= 0x0AFF for c in english_text):
        return english_text
    
    # Special exception: Replace "Vadhel" with "વઢેળ" (case-insensitive)
    vadhel_pattern = re.compile(r'\bvadhel\b', re.IGNORECASE)
    
    # Check if Vadhel is present
    has_vadhel = vadhel_pattern.search(english_text)
    
    # Try to use Google Translate API with timeout protection
    try:
        # Replace Vadhel with a unique marker that won't be translated
        # Using a numeric code that Google Translate will preserve
        text_to_translate = vadhel_pattern.sub('XXX999XXX', english_text) if has_vadhel else english_text
        
        # Use timeout to prevent hanging (3 seconds should be enough for translation)
        with time_limit(3):
            result = translator.translate(text_to_translate, src='en', dest='gu')
            translated_text = result.text if result and result.text else None
        
        # If translation succeeded, process it
        if translated_text:
            # Replace the marker with the correct Gujarati text
            if has_vadhel:
                # Replace our marker
                translated_text = translated_text.replace('XXX999XXX', 'વઢેળ')
                # Also try other variations that might have been translated
                translated_text = translated_text.replace('વાધેલ', 'વઢેળ')
                translated_text = translated_text.replace('વધેલ', 'વઢેળ')
                # Clean up any remaining placeholder artifacts from old code/existing data
                translated_text = re.sub(r'_?પ્લેસહોલ્ડર', '', translated_text)
            
            return translated_text
    except (TimeoutException, Exception) as e:
        # Log the error for debugging
        error_type = "timed out" if isinstance(e, TimeoutException) else "failed"
        print(f"Google Translate {error_type}: {e}. Using fallback translation.")
    
    # Fallback to dictionary-based translation if Google Translate fails or times out
    print("Using dictionary-based fallback translation.")
    
    # Convert to lowercase for matching
    text_lower = english_text.lower().strip()
    result = text_lower
    
    # Replace words with Gujarati equivalents from dictionary (including vadhel)
    for eng, guj in ENGLISH_TO_GUJARATI.items():
        # Use word boundary replacement to avoid partial matches
        result = re.sub(r'\b' + eng + r'\b', guj, result, flags=re.IGNORECASE)
    
    # If we replaced something, return it
    if any(ord(c) >= 0x0A80 and ord(c) <= 0x0AFF for c in result):
        return result
    
    # Otherwise return original
    return english_text


@app.route('/')
def index():
    """Main page with guest name entry and sender selection"""
    return render_template('index.html', senders=WHATSAPP_SENDERS)


@app.route('/translate', methods=['POST'])
def translate_name():
    """API endpoint to translate name from English to Gujarati"""
    data = request.get_json()
    name_english = data.get('name_english', '').strip()
    
    if not name_english:
        return jsonify({'success': False, 'error': 'Name is required'})
    
    # Auto-translate to Gujarati
    name_gujarati = transliterate_to_gujarati(name_english)
    
    return jsonify({'success': True, 'name_gujarati': name_gujarati})


@app.route('/get-pdf')
def get_pdf():
    """Return the PDF template as-is"""
    template_pdf = 'Invitation card.pdf'
    
    if not os.path.exists(template_pdf):
        return jsonify({'success': False, 'error': 'PDF template not found'}), 404
    
    try:
        # Return the PDF template as-is
        return send_file(
            template_pdf,
            as_attachment=False,
            download_name="Vadhel Sarthak's Wedding Invitation.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error sending PDF: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to send PDF'}), 500


if __name__ == '__main__':
    # Run the app (debug mode should be disabled in production)
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
