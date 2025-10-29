# Docker Deployment Guide

This guide provides detailed instructions for deploying the Invitation Card Automation application using Docker.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start with Docker Compose](#quick-start-with-docker-compose)
- [Manual Docker Commands](#manual-docker-commands)
- [Digital Ocean Deployment](#digital-ocean-deployment)
- [Configuration](#configuration)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- At least 512MB of free RAM
- Port 5000 available

### Installing Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Install Docker Compose Plugin
```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

## Quick Start with Docker Compose

The easiest way to run the application:

```bash
# Clone the repository
git clone https://github.com/sarthakvadhel/Invitation-card-automation-WhatsApp.git
cd Invitation-card-automation-WhatsApp

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Open http://localhost:5000 in your browser
```

## Manual Docker Commands

### Building the Image

```bash
docker build -t invitation-card-app .
```

### Running the Container

**Basic run (without persistence):**
```bash
docker run -d -p 5000:5000 --name invitation-app invitation-card-app
```

**With persistent database (recommended):**
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --name invitation-app \
  invitation-card-app
```

**With custom environment variables:**
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e FLASK_DEBUG=False \
  --name invitation-app \
  invitation-card-app
```

### Container Management

**View logs:**
```bash
docker logs -f invitation-app
```

**Stop container:**
```bash
docker stop invitation-app
```

**Start stopped container:**
```bash
docker start invitation-app
```

**Restart container:**
```bash
docker restart invitation-app
```

**Remove container:**
```bash
docker stop invitation-app
docker rm invitation-app
```

**Access container shell:**
```bash
docker exec -it invitation-app /bin/bash
```

## Digital Ocean Deployment

### Step-by-Step Guide for Ubuntu Droplet

1. **Create a Digital Ocean Droplet**
   - Choose Ubuntu 22.04 or later
   - Select at least the $6/month plan (1GB RAM)
   - Note your droplet's IP address

2. **SSH into your droplet**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Update system packages**
   ```bash
   apt-get update
   apt-get upgrade -y
   ```

4. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

5. **Install Docker Compose**
   ```bash
   apt-get install docker-compose-plugin -y
   ```

6. **Clone the repository**
   ```bash
   git clone https://github.com/sarthakvadhel/Invitation-card-automation-WhatsApp.git
   cd Invitation-card-automation-WhatsApp
   ```

7. **Deploy the application**
   ```bash
   docker-compose up -d
   ```

8. **Verify deployment**
   ```bash
   docker-compose ps
   docker-compose logs
   ```

9. **Access your application**
   - Open: `http://your-droplet-ip:5000`

### Setting up Auto-Restart on Boot

The `docker-compose.yml` file already includes `restart: unless-stopped`, which means:
- Container automatically restarts if it crashes
- Container starts automatically when the server boots
- Container won't restart if you manually stop it

### Optional: Setup Nginx Reverse Proxy

For production, you may want to use Nginx as a reverse proxy:

1. **Install Nginx**
   ```bash
   apt-get install nginx -y
   ```

2. **Create Nginx configuration**
   ```bash
   cat > /etc/nginx/sites-available/invitation-app << 'EOF'
   server {
       listen 80;
       server_name your-domain.com;  # or your-droplet-ip

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   EOF
   ```

3. **Enable the configuration**
   ```bash
   ln -s /etc/nginx/sites-available/invitation-app /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

Now access your app at `http://your-domain.com` (port 80).

## Configuration

### Environment Variables

You can customize the application using environment variables:

```yaml
# In docker-compose.yml
environment:
  - FLASK_DEBUG=False           # Set to True for development
  - SECRET_KEY=your-secret-key  # Custom secret key
```

### Volume Mounts

The application uses volumes for data persistence:

```yaml
volumes:
  - ./data:/app/data  # Database directory persistence
```

The database file (`invitations.db`) is stored in the `data/` directory, which is mounted as a volume. This ensures:
- Data persists across container restarts
- Database file is accessible from the host machine
- No permission issues when creating the database

### Customizing Gunicorn

Edit the `Dockerfile` CMD line to adjust Gunicorn settings:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

- `--workers 4`: Number of worker processes (adjust based on CPU cores)
- `--timeout 120`: Request timeout in seconds
- For a 1GB RAM droplet, 2-4 workers is recommended

## Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or with manual docker commands
docker stop invitation-app
docker rm invitation-app
docker build -t invitation-card-app .
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data --name invitation-app invitation-card-app
```

### Backup Database

```bash
# Copy database from running container
docker cp invitation-app:/app/data/invitations.db ./backup-invitations-$(date +%Y%m%d).db

# Or if using volume mount (recommended)
cp data/invitations.db backup-invitations-$(date +%Y%m%d).db
```

### Restore Database

```bash
# Stop the container
docker-compose down

# Restore database
cp backup-invitations-YYYYMMDD.db data/invitations.db

# Start the container
docker-compose up -d
```

### Viewing Resource Usage

```bash
# View container resource usage
docker stats invitation-app

# View all containers
docker stats
```

## Troubleshooting

### Container won't start

**Check logs:**
```bash
docker-compose logs
# or
docker logs invitation-app
```

**Check container status:**
```bash
docker ps -a
```

### Port already in use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process or change the port in docker-compose.yml
```

### Database permission issues

```bash
# Fix permissions for the data directory
sudo chown -R 1000:1000 data/

# Or recreate the database
docker exec -it invitation-app rm /app/data/invitations.db
docker restart invitation-app
```

### Container keeps restarting

```bash
# Check logs for errors
docker logs invitation-app

# Check health status
docker inspect invitation-app | grep -A 10 Health
```

### Out of disk space

```bash
# Clean up unused images and containers
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Cannot access from external IP

1. **Check firewall:**
   ```bash
   # On Ubuntu/Debian
   sudo ufw allow 5000/tcp
   sudo ufw status
   ```

2. **Check Digital Ocean firewall settings**
   - Go to Digital Ocean dashboard
   - Navigate to Networking → Firewalls
   - Ensure port 5000 is allowed

3. **Verify container is listening on all interfaces:**
   ```bash
   docker logs invitation-app | grep "Listening at"
   # Should show: Listening at: http://0.0.0.0:5000
   ```

### Need to reset everything

```bash
# Complete cleanup
docker-compose down
docker rmi invitation-card-app
rm -rf data/

# Fresh start
docker-compose up -d --build
```

## Performance Tuning

### For Production Deployment

1. **Adjust Gunicorn workers based on CPU cores:**
   - Formula: (2 × CPU cores) + 1
   - 1 CPU → 3 workers
   - 2 CPU → 5 workers

2. **Monitor resource usage:**
   ```bash
   docker stats invitation-app
   ```

3. **Set resource limits (optional):**
   ```yaml
   # In docker-compose.yml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
       reservations:
         memory: 256M
   ```

## Security Best Practices

1. **Keep Docker updated:**
   ```bash
   apt-get update
   apt-get upgrade docker-ce docker-ce-cli containerd.io
   ```

2. **Use environment variables for secrets:**
   ```bash
   # Create .env file (don't commit to git!)
   echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
   ```

3. **Enable firewall:**
   ```bash
   ufw allow 22/tcp   # SSH
   ufw allow 5000/tcp # Application
   ufw enable
   ```

4. **Regular backups:**
   Set up a cron job for automated backups:
   ```bash
   # Add to crontab (crontab -e)
   0 2 * * * cd /root/Invitation-card-automation-WhatsApp && cp data/invitations.db backup-$(date +\%Y\%m\%d).db
   ```

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Review this troubleshooting guide
3. Open an issue on GitHub with:
   - Docker version (`docker --version`)
   - Docker Compose version (`docker-compose --version`)
   - Error logs
   - Steps to reproduce

---

**Happy Deploying! 🎉**
