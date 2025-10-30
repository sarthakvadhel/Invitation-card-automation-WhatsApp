# Wedding Invitation Sender

A simple web application to send personalized wedding invitations via WhatsApp with automatic English to Gujarati translation.

## Features

- **Single-Page Interface**: Simple and clean UI with guest name entry
- **Automatic Translation**: English names are automatically translated to Gujarati
- **Multiple Senders**: Choose from 3 sender options (Sarthak, Vanrajbhai, Vasudha)
- **WhatsApp Integration**: Direct sharing via WhatsApp Web Share API or manual sharing
- **No Database**: Lightweight application with no data persistence
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/sarthakvadhel/Invitation-card-automation-WhatsApp.git
   cd Invitation-card-automation-WhatsApp
   ```

2. **Start the application**
   ```bash
   docker compose up -d
   ```

3. **Access the application**
   
   Open your browser and navigate to: `http://localhost:5000`

4. **Stop the application**
   ```bash
   docker compose down
   ```

### Using Python Directly

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Access the application**
   
   Open your browser and navigate to: `http://localhost:5000`

## How to Use

1. **Enter Guest Name**: Type the guest's name in English (e.g., "Ramesh Patel")
2. **Automatic Translation**: The name will be automatically translated to Gujarati
3. **Select Sender**: Click one of the three sender buttons:
   - 📱 Sarthak
   - 📱 Vanrajbhai
   - 📱 Vasudha
4. **Send via WhatsApp**: 
   - On mobile: WhatsApp app will open with the invitation PDF and greeting message
   - On desktop: WhatsApp Web will open with the message; you'll need to manually attach the PDF

## Technical Details

### Application Structure

```
.
├── app.py                    # Main Flask application
├── templates/
│   └── index.html           # Single-page web interface
├── Invitation card.pdf      # Wedding invitation template
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker container configuration
└── docker-compose.yml      # Docker Compose configuration
```

### Dependencies

- **Flask**: Web framework
- **googletrans**: English to Gujarati translation
- **gunicorn**: Production WSGI server (for Docker deployment)

### Translation System

The application uses a two-tier translation system:

1. **Google Translate API**: Primary translation method
2. **Dictionary-based Fallback**: Uses a pre-defined dictionary for common names and words when Google Translate is unavailable

### Greeting Message Format

When you select a sender, the following message is sent via WhatsApp:

```
નમસ્તે [Guest Name in Gujarati],
આપને અને આપના પરિવારને અમારા લગ્ન સમારોહમાં આમંત્રિત કરવા માટે આનંદ થાય છે.
કૃપા કરીને આમંત્રણ કાર્ડ ને રૂબરૂ મળ્યા તુલ્ય સમજી આ વઢેળ પરિવારના તેડાને સ્વીકારીને 
અમારા પ્રસંગમાં અભિવૃધ્ધિ કરશોજી.

સાદર,
[Sender Name]
```

## Docker Configuration

### Building the Image

```bash
docker build -t invitation-app .
```

### Running the Container

```bash
docker run -d -p 5000:5000 --name invitation-card-app invitation-app
```

### Using Docker Compose

```bash
# Start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Development

### Project Requirements

- Python 3.12 or higher
- Docker (optional, for containerized deployment)

### Environment Variables

- `FLASK_DEBUG`: Set to `True` for development mode (default: `False`)

### Customization

To customize the greeting message, edit the `sendInvitation()` function in `templates/index.html`.

To add more sender options, update the `WHATSAPP_SENDERS` dictionary in `app.py` and add corresponding buttons in `templates/index.html`.

## Browser Compatibility

- **Best Experience**: Chrome/Edge on Android (supports Web Share API with files)
- **Desktop**: Chrome, Firefox, Edge, Safari (requires manual PDF attachment)
- **Mobile**: Chrome, Safari, Firefox (may require manual PDF attachment on iOS)

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, you can change it:

**Docker Compose:**
Edit `docker-compose.yml` and change `"5000:5000"` to `"8080:5000"` (or any other port)

**Python:**
Edit `app.py` and change the port in `app.run(host='0.0.0.0', port=5000)`

### Translation Not Working

If Google Translate fails, the application automatically falls back to dictionary-based translation. Common names and words are already included in the dictionary.

To add more words to the dictionary, edit the `ENGLISH_TO_GUJARATI` dictionary in `app.py`.

## License

This project is open-source and available for personal use.

## Support

For issues or questions, please open an issue on GitHub.
