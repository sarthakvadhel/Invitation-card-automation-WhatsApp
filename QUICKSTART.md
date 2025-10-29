# Quick Deployment Guide for Digital Ocean

This is a quick reference for deploying to your Digital Ocean droplet at http://159.89.175.226:5000

> **Note:** This guide uses your specific droplet IP (159.89.175.226). If you're using a different server, replace this IP with your server's address.

## Initial Deployment

```bash
# 1. SSH into your droplet
ssh root@159.89.175.226

# 2. Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Clone this repository
git clone https://github.com/sarthakvadhel/Invitation-card-automation-WhatsApp.git
cd Invitation-card-automation-WhatsApp

# 4. Deploy the application
docker compose up -d

# 5. Verify it's running
docker compose ps
docker compose logs

# 6. Access your application
# Open http://159.89.175.226:5000 in your browser
```

## Managing the Application

```bash
# View logs
docker compose logs -f

# Restart the application
docker compose restart

# Stop the application
docker compose down

# Update the application
git pull origin main
docker compose up -d --build
```

## Backup Database

```bash
# The database is in the project directory (mounted as volume)
# Make sure you're in the project directory
cd ~/Invitation-card-automation-WhatsApp

# Create a backup
cp invitations.db backup-invitations-$(date +%Y%m%d).db

# List backups
ls -lh backup-*.db
```

## Troubleshooting

```bash
# If port 5000 is blocked
sudo ufw allow 5000/tcp
sudo ufw status

# Check container status
docker compose ps

# View detailed logs
docker compose logs --tail=100

# Restart everything
docker compose down
docker compose up -d --build
```

## Complete Reset (if needed)

```bash
# Make sure you're in the project directory
cd ~/Invitation-card-automation-WhatsApp

# Stop and remove everything
docker compose down
docker system prune -a -f

# Remove database (WARNING: This deletes all data!)
rm invitations.db

# Fresh start
docker compose up -d --build
```

---

**Quick Tips:**
- Application runs on port 5000
- Database is persisted in `invitations.db` file
- Logs available via `docker compose logs`
- Auto-restarts on server reboot (configured with `restart: unless-stopped`)
- Uses Gunicorn with 4 workers for production stability
