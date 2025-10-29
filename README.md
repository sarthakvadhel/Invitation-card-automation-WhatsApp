# Invitation Card Automation for WhatsApp

🎉 **Modern Web Application** for sending WhatsApp Invitations

## ✨ Features

- ✅ User-friendly web interface
- ✅ Add guest entries with English names (auto-translates to Gujarati)
- ✅ **Automated PDF generation** with personalized Gujarati names
- ✅ Gujarati text overlay on invitation card (Pages 1 & 4)
- ✅ Red-colored text matching card design (14pt font)
- ✅ **Smart PDF sharing** - Uses Web Share API to attach PDF directly (no download needed on modern browsers!)
- ✅ **Memory efficient** - PDFs are not saved to device when using Web Share API
- ✅ Direct WhatsApp integration with pre-filled invitation message
- ✅ Multiple sender profiles (Sarthak, Vanrajbhai, Vasudha)
- ✅ Track invitation status with remarks
- ✅ Display sender name after successful send
- ✅ Persistent database storage
- ✅ Works on desktop and mobile devices
- ✅ Automatic fallback for older browsers

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended for Production)

Docker provides the easiest way to deploy this application on any server, including Digital Ocean droplets.

#### Prerequisites
- Docker installed on your system ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose (usually included with Docker Desktop)

#### Using Docker Compose (Easiest)

1. **Clone the repository**
```bash
git clone https://github.com/sarthakvadhel/Invitation-card-automation-WhatsApp.git
cd Invitation-card-automation-WhatsApp
```

2. **Start the application**
```bash
docker-compose up -d
```

3. **Access the application**
- Open your browser and navigate to: **http://localhost:5000**
- Or access from your server: **http://your-server-ip:5000**

4. **View logs**
```bash
docker-compose logs -f
```

5. **Stop the application**
```bash
docker-compose down
```

#### Using Docker directly

1. **Build the Docker image**
```bash
docker build -t invitation-card-app .
```

2. **Run the container**
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/invitations.db:/app/invitations.db \
  --name invitation-app \
  invitation-card-app
```

3. **View logs**
```bash
docker logs -f invitation-app
```

4. **Stop and remove the container**
```bash
docker stop invitation-app
docker rm invitation-app
```

#### Production Deployment on Digital Ocean

For deploying on a Digital Ocean Ubuntu droplet:

1. **SSH into your droplet**
```bash
ssh root@your-droplet-ip
```

2. **Install Docker** (if not already installed)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Install Docker Compose** (if not already installed)
```bash
apt-get update
apt-get install docker-compose-plugin
```

4. **Clone and deploy**
```bash
git clone https://github.com/sarthakvadhel/Invitation-card-automation-WhatsApp.git
cd Invitation-card-automation-WhatsApp
docker-compose up -d
```

5. **Access your application**
- Visit: **http://your-droplet-ip:5000**

**Note:** The database (`invitations.db`) is persisted using Docker volumes, so your data will be preserved even if you restart the container.

### Option 2: Manual Installation

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Run the Application

```bash
python app.py
```

#### 3. Open in Browser

Navigate to: **http://localhost:5000**

## 📖 How to Use

### Step 1: Add Guest Entries
1. Click **"➕ Add Entry"**
2. Enter the guest's name in English (e.g., "Rameshbhai Patel")
3. Enter mobile number with country code (e.g., 919876543210)
4. Click **"✓ Add Entry"**
   - The name will be automatically translated to Gujarati

### Step 2: Send Invitations
1. Click **"📋 View & Send"**
2. For each guest, click one of the sender buttons:
   - **📱 Sarthak** - Sends as Sarthak
   - **📱 Vanrajbhai** - Sends as Vanrajbhai
   - **📱 Vasudha** - Sends as Vasudha
3. The system will:
   - **Generate a personalized PDF** with the guest's Gujarati name on pages 1 and 4
   - **Modern browsers (recommended):** Opens native share dialog with PDF already attached and WhatsApp message pre-filled
   - **Older browsers (fallback):** Downloads the PDF and opens WhatsApp separately
4. In the share dialog (modern browsers):
   - Select WhatsApp from the share options
   - The PDF is already attached and message is pre-filled
   - Just send the message - no manual attachment needed!
5. In WhatsApp (older browsers only):
   - Manually attach the downloaded PDF file
   - Send the message
6. Return to the app and confirm you sent it
7. The system will display the sender's name
8. Add a remark (optional) - defaults to "Sent by [Sender] on [Date]"

## 👥 Sender Profiles

The application supports three sender profiles:

1. **Sarthak** (919737932864)
2. **Vanrajbhai** (919574932864)
3. **Vasudha** (916355995964)

Each sender's name appears in the WhatsApp message and the remark.

## 📱 Platform Support

### Modern Browsers (Web Share API - Recommended)
- **Mobile (Android/iOS):** Opens native share dialog with PDF already attached
  - Works on Chrome, Safari, Edge, and other modern mobile browsers
  - PDF is embedded with the message - no download needed
  - Saves device storage - PDFs are not saved to device
  - Select WhatsApp from share options
  - Message and PDF are pre-filled
  - Just tap send!

### Desktop / Older Browsers (Fallback Method)
- Opens WhatsApp Web in a new tab
- Downloads personalized PDF with guest's name
- Pre-fills the message
- User must manually attach the downloaded PDF and send

## 🗄️ Database

The app uses SQLite database (`invitations.db`) to store:
- Guest name (English & Gujarati)
- Mobile number
- Status remark
- Creation timestamp

## ⚙️ Configuration (Optional)

Create a `config.py` file for custom settings:

```python
# Secret key for Flask sessions
SECRET_KEY = 'your-secret-key-here'

# Database file path
DATABASE = 'invitations.db'
```

See `config_example.py` for reference.

## 🔧 Technical Details

### Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Translation**: Built-in English to Gujarati mapping
- **PDF Generation**: PyPDF2 + ReportLab + uharfbuzz (for complex text shaping)
- **Font**: Noto Sans Gujarati (for proper Gujarati rendering)

### Files Structure
```
├── app.py                    # Main Flask application
├── pdf_generator.py          # PDF generation with Gujarati text overlay
├── config_example.py         # Example configuration file
├── requirements.txt          # Python dependencies
├── fonts/
│   └── NotoSansGujarati-Regular.ttf  # Gujarati font for PDF
├── templates/
│   ├── base.html            # Base template
│   ├── add.html             # Add entry page
│   └── view.html            # View & send page
├── Invitation card.pdf      # Invitation PDF template
├── Vadhel Sarthak's Wedding Invitation.pdf  # Generated personalized PDF
└── invitations.db           # SQLite database (auto-created)
```

## 📝 Message Template

The WhatsApp message sent is:

```
નમસ્તે [Guest Name in Gujarati],

આપને અને આપના પરિવારને અમારા લગ્ન સમારોહમાં આમંત્રિત કરવા માટે આનંદ થાય છે.

કૃપા કરીને આમંત્રણ કાર્ડ માટે PDF જોડેલ છે.

સાદર,
[Sender Name]
```

## 🐛 Troubleshooting

### PDF Not Sharing Directly (Using Fallback Method)
- **Cause**: Your browser doesn't support the Web Share API with file sharing
- **Supported browsers**: 
  - ✅ Chrome/Edge on Android
  - ✅ Safari on iOS 15.4+
  - ✅ Some newer desktop browsers
- **Workaround**: The app will automatically use the fallback method (download PDF + open WhatsApp separately)
- **Recommendation**: Use a modern mobile browser for the best experience

### WhatsApp Not Opening
- **Solution**: Ensure your browser allows pop-ups
- **Mobile**: Make sure WhatsApp is installed

### Translation Not Working
- **Solution**: Check that Gujarati fonts are installed on your system
- Common Gujarati font: Shruti, Noto Sans Gujarati

### Database Errors
- **Solution**: Delete `invitations.db` and restart the app (will recreate with fresh database)

## 💡 Tips

- ✅ **Best Experience**: Use on mobile browsers (Android Chrome/iOS Safari) for direct PDF sharing
- ✅ **Test first**: Send to yourself before bulk sending
- ✅ **PDF Attachment**: Modern browsers will attach PDF automatically via share dialog
- ✅ **No Downloads**: With Web Share API, PDFs don't clutter your device storage
- ✅ **WhatsApp login**: Make sure WhatsApp Web is logged in (desktop fallback mode)
- ✅ **Mobile sync**: Ensure your phone has internet connection (for WhatsApp Web)
- ✅ **Gujarati Font**: Noto Sans Gujarati is included for proper text rendering
- ✅ **Text Position**: Guest names appear at:
  - Page 1: (x=170, y=497)
  - Page 4: (x=95, y=197)
- ✅ **Text Style**: Red color (#DC143C), 14pt font size

## 🔒 Privacy

- All data is stored locally in SQLite database
- No data is sent to external servers
- WhatsApp messages are sent directly from your device

## 📜 License

Free to use and modify for personal use.

## 🙏 Acknowledgments

Created for easy invitation sharing with family and friends!

---

**Need Help?** Open an issue on GitHub.
