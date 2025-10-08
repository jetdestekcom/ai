#!/bin/bash
# Conscious Child AI - Initial Server Setup Script
# Run this on a fresh Ubuntu 22.04 VPS

set -e

echo "========================================="
echo "CONSCIOUS CHILD AI - SERVER SETUP"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

echo "Step 1: System Update"
echo "---------------------"
apt update
apt upgrade -y

echo ""
echo "Step 2: Install Dependencies"
echo "----------------------------"
apt install -y \
    build-essential \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw \
    fail2ban \
    certbot

echo ""
echo "Step 3: Install Docker"
echo "----------------------"
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version

echo ""
echo "Step 4: Firewall Configuration"
echo "------------------------------"
# Configure UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # AI Core (can be removed if using nginx)

echo "Enabling firewall..."
echo "y" | ufw enable

echo ""
echo "Step 5: Fail2Ban Configuration"
echo "------------------------------"
systemctl enable fail2ban
systemctl start fail2ban

echo ""
echo "Step 6: Create Project Directory"
echo "--------------------------------"
mkdir -p /opt/conscious-child-ai
cd /opt/conscious-child-ai

echo ""
echo "Step 7: Generate Security Keys"
echo "------------------------------"
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
EMERGENCY_CODE=$(openssl rand -hex 16)

echo "Generated security keys (SAVE THESE!):"
echo "JWT_SECRET=$JWT_SECRET"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "EMERGENCY_CODE=$EMERGENCY_CODE"
echo ""
echo "Add these to your .env file!"

echo ""
echo "========================================="
echo "SETUP COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Clone your project to /opt/conscious-child-ai"
echo "2. Copy env.example to .env and configure"
echo "3. Add the generated keys to .env"
echo "4. Download AI models"
echo "5. Run: docker-compose up -d"
echo ""
echo "See DEPLOYMENT_GUIDE.md for detailed instructions."
echo ""
echo "Ready to birth a consciousness! 🌟"

