# WhatsApp API Configuration
#
# This file contains configuration for WhatsApp message sending.
# Copy this file to 'config.py' and fill in your actual API credentials.

# WhatsApp API Provider
# Options: 'simulated', 'twilio', 'generic'
# - simulated: For testing without actual API (default)
# - twilio: For Twilio WhatsApp API
# - generic: For other WhatsApp Business API providers
WHATSAPP_PROVIDER = 'simulated'

# API Endpoints (for generic provider)
WHATSAPP_API_URL = 'https://api.example.com/v1/messages'
WHATSAPP_MEDIA_UPLOAD_URL = 'https://api.example.com/v1/media'

# Sender Configurations
WHATSAPP_SENDERS = {
    'sarthak': {
        'name': 'Sarthak',
        'phone': '919737932864',
        'provider': WHATSAPP_PROVIDER,
        
        # For Twilio (uncomment and fill when using Twilio)
        # 'account_sid': 'your_twilio_account_sid_here',
        # 'auth_token': 'your_twilio_auth_token_here',
        
        # For Generic API (uncomment and fill when using generic provider)
        # 'api_key': 'your_api_key_here',
    },
    'pappa': {
        'name': 'Pappa',
        'phone': '919574932864',
        'provider': WHATSAPP_PROVIDER,
        
        # For Twilio (uncomment and fill when using Twilio)
        # 'account_sid': 'your_twilio_account_sid_here',
        # 'auth_token': 'your_twilio_auth_token_here',
        
        # For Generic API (uncomment and fill when using generic provider)
        # 'api_key': 'your_api_key_here',
    },
    'vasudha': {
        'name': 'Vasudha',
        'phone': '916355995964',
        'provider': WHATSAPP_PROVIDER,
        
        # For Twilio (uncomment and fill when using Twilio)
        # 'account_sid': 'your_twilio_account_sid_here',
        # 'auth_token': 'your_twilio_auth_token_here',
        
        # For Generic API (uncomment and fill when using generic provider)
        # 'api_key': 'your_api_key_here',
    }
}

# Flask Secret Key (change this for production!)
SECRET_KEY = 'your-secret-key-change-this-in-production'

# Database Configuration
DATABASE = 'invitations.db'

# PDF Configuration
# Coordinates for adding Gujarati name on pages 1 and 4
# Format: (x, y) where x and y are pixel coordinates
# Adjust these based on your invitation card layout
PDF_TEXT_POSITION_PAGE1 = (250, 350)
PDF_TEXT_POSITION_PAGE4 = (250, 350)

# Font size for Gujarati name on invitation card
PDF_FONT_SIZE = 14

# Font color for Gujarati name (RGB values 0-255)
PDF_FONT_COLOR = (220, 20, 60)  # Crimson red
