#!/usr/bin/env python3
"""
Invitation Card Web Application
Flask-based web app for managing and sending invitation cards via WhatsApp
"""

import os
import re
import sqlite3
import traceback
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from pdf_generator import InvitationPDFGenerator
from googletrans import Translator
import signal
from contextlib import contextmanager

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


# Try to load config from config.py, otherwise use defaults
try:
    from config import SECRET_KEY, DATABASE
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DATABASE'] = DATABASE
except ImportError:
    # Use default configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    # Use data directory for database to ensure proper permissions in Docker
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    app.config['DATABASE'] = os.path.join(data_dir, 'invitations.db')

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

# WhatsApp sender configurations (loaded from whatsapp_integration module)
WHATSAPP_SENDERS = {
    'sarthak': {
        'name': 'Sarthak',
        'phone': '919737932864',
    },
    'vanrajbhai': {
        'name': 'Vanrajbhai',
        'phone': '919574932864',
    },
    'vasudha': {
        'name': 'Vasudha',
        'phone': '916355995964',
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
                # This can be removed once all existing entries have been migrated/cleaned
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


def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize the database"""
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_english TEXT NOT NULL,
            name_gujarati TEXT NOT NULL,
            mobile TEXT,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
    db.close()


# Initialize database on app startup (regardless of how it's run)
init_db()


@app.route('/')
def index():
    """Redirect to add entry page"""
    return redirect(url_for('add_entry'))


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    """Page 1: Form to add entry"""
    if request.method == 'POST':
        try:
            name_english = request.form.get('name_english', '').strip()
            mobile = request.form.get('mobile', '').strip()
            
            if not name_english:
                return render_template('add.html', error='Name is required')
            
            # Auto-translate to Gujarati
            name_gujarati = transliterate_to_gujarati(name_english)
            
            # Save to database (mobile can be empty)
            db = get_db()
            db.execute(
                'INSERT INTO invitations (name_english, name_gujarati, mobile) VALUES (?, ?, ?)',
                (name_english, name_gujarati, mobile if mobile else None)
            )
            db.commit()
            db.close()
            
            return redirect(url_for('view_entries'))
        except Exception as e:
            # Log the error for debugging
            print(f"Error adding entry: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            
            # Return user-friendly error message
            return render_template('add.html', error='An error occurred while adding the entry. Please try again.')
    
    return render_template('add.html')


@app.route('/view')
def view_entries():
    """Page 2: Table view with WhatsApp sending buttons"""
    db = get_db()
    entries = db.execute('SELECT * FROM invitations ORDER BY id DESC').fetchall()
    db.close()
    
    return render_template('view.html', entries=entries, senders=WHATSAPP_SENDERS)


@app.route('/update-remark/<int:entry_id>', methods=['POST'])
def update_remark(entry_id):
    """Update remark for an entry after manual WhatsApp send"""
    data = request.get_json()
    remark = data.get('remark', '').strip()
    
    # Remark is optional - allow empty string
    # If user cancels the prompt, we don't update anything (handled in frontend)
    
    db = get_db()
    
    # Check if entry exists
    entry = db.execute('SELECT * FROM invitations WHERE id = ?', (entry_id,)).fetchone()
    if not entry:
        db.close()
        return jsonify({'success': False, 'error': 'Entry not found'})
    
    # Update the remark
    db.execute('UPDATE invitations SET remark = ? WHERE id = ?', (remark, entry_id))
    db.commit()
    db.close()
    
    return jsonify({'success': True})


@app.route('/update-mobile/<int:entry_id>', methods=['POST'])
def update_mobile(entry_id):
    """Update mobile number for an entry"""
    data = request.get_json()
    mobile = data.get('mobile', '').strip()
    
    db = get_db()
    
    # Check if entry exists
    entry = db.execute('SELECT * FROM invitations WHERE id = ?', (entry_id,)).fetchone()
    if not entry:
        db.close()
        return jsonify({'success': False, 'error': 'Entry not found'})
    
    # Update the mobile number
    db.execute('UPDATE invitations SET mobile = ? WHERE id = ?', (mobile if mobile else None, entry_id))
    db.commit()
    db.close()
    
    return jsonify({'success': True})


@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Delete an entry"""
    db = get_db()
    db.execute('DELETE FROM invitations WHERE id = ?', (entry_id,))
    db.commit()
    db.close()
    
    return jsonify({'success': True})


@app.route('/generate-pdf/<int:entry_id>')
def generate_pdf(entry_id):
    """Generate personalized PDF for an entry and return as downloadable file"""
    db = get_db()
    entry = db.execute('SELECT * FROM invitations WHERE id = ?', (entry_id,)).fetchone()
    db.close()
    
    if not entry:
        return jsonify({'success': False, 'error': 'Entry not found'}), 404
    
    # Get Gujarati name
    gujarati_name = entry['name_gujarati']
    
    # Generate the PDF in memory (not saved to disk)
    try:
        pdf_generator = InvitationPDFGenerator()
        pdf_bytes = pdf_generator.generate_personalized_invitation(gujarati_name, return_bytes=True)
        
        # Return the PDF file for download directly from memory
        return send_file(
            pdf_bytes,
            as_attachment=True,
            download_name="Vadhel Sarthak's Wedding Invitation.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to user
        print(f"Error generating PDF for entry {entry_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500


@app.route('/generate-pdf-blob/<int:entry_id>')
def generate_pdf_blob(entry_id):
    """Generate personalized PDF for an entry and return as inline file for Web Share API"""
    db = get_db()
    entry = db.execute('SELECT * FROM invitations WHERE id = ?', (entry_id,)).fetchone()
    db.close()
    
    if not entry:
        return jsonify({'success': False, 'error': 'Entry not found'}), 404
    
    # Get Gujarati name
    gujarati_name = entry['name_gujarati']
    
    # Generate the PDF in memory (not saved to disk)
    try:
        pdf_generator = InvitationPDFGenerator()
        pdf_bytes = pdf_generator.generate_personalized_invitation(gujarati_name, return_bytes=True)
        
        # Return the PDF file as inline (not as attachment) so it can be used by Web Share API
        return send_file(
            pdf_bytes,
            as_attachment=False,
            download_name="Vadhel Sarthak's Wedding Invitation.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to user
        print(f"Error generating PDF for entry {entry_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500


if __name__ == '__main__':
    # Run the app (debug mode should be disabled in production)
    # Set debug=False for production deployment
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
