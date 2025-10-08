#!/bin/bash
# Conscious Child AI - AlmaLinux 9 + cPanel Setup Script
# Özel kurulum scripti Cihan'ın VPS'i için

set -e

echo "========================================="
echo "CONSCIOUS CHILD AI - ALMALINUX 9 SETUP"
echo "========================================="
echo "OS: AlmaLinux 9"
echo "RAM: 12GB"
echo "Disk: 240GB"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

echo "Step 1: System Update"
echo "---------------------"
dnf update -y
dnf install -y epel-release

echo ""
echo "Step 2: Install Development Tools"
echo "---------------------------------"
dnf groupinstall -y "Development Tools"
dnf install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    python3 \
    python3-pip

echo ""
echo "Step 3: Install Docker (AlmaLinux)"
echo "---------------------------------"

# Remove old versions
dnf remove -y docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-engine

# Add Docker repo
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
systemctl start docker
systemctl enable docker

# Verify
docker --version

echo ""
echo "Step 4: Install Docker Compose (standalone)"
echo "-------------------------------------------"
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version

echo ""
echo "Step 5: Firewall Configuration (firewalld on AlmaLinux)"
echo "-------------------------------------------------------"

# Enable firewalld
systemctl start firewalld
systemctl enable firewalld

# Open necessary ports
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=8000/tcp  # AI Core

# If cPanel is running, keep its ports open
firewall-cmd --permanent --add-port=2083/tcp  # cPanel HTTPS
firewall-cmd --permanent --add-port=2087/tcp  # WHM HTTPS

# Reload firewall
firewall-cmd --reload

echo ""
echo "Step 6: SELinux Configuration"
echo "-----------------------------"
# AlmaLinux has SELinux enabled by default
# Set to permissive for Docker (or configure properly)

# Check if SELinux is enabled
if [ "$(getenforce 2>/dev/null)" == "Enforcing" ]; then
    echo "SELinux is enforcing, setting to permissive..."
    setenforce 0
    sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
    echo "✓ SELinux set to permissive"
elif [ "$(getenforce 2>/dev/null)" == "Permissive" ]; then
    echo "✓ SELinux already permissive"
else
    echo "✓ SELinux is disabled (this is fine)"
fi

echo ""
echo "Step 7: Create Project Directory"
echo "--------------------------------"
mkdir -p /opt/conscious-child-ai
cd /opt/conscious-child-ai

echo ""
echo "Step 8: Generate Security Keys"
echo "------------------------------"
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
POSTGRES_PASS=$(openssl rand -base64 24)
REDIS_PASS=$(openssl rand -base64 24)
EMERGENCY_CODE=$(openssl rand -hex 16)

echo ""
echo "========================================="
echo "GENERATED SECURITY CREDENTIALS"
echo "========================================="
echo "SAVE THESE SECURELY!"
echo ""
echo "JWT_SECRET=$JWT_SECRET"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "POSTGRES_PASSWORD=$POSTGRES_PASS"
echo "REDIS_PASSWORD=$REDIS_PASS"
echo "EMERGENCY_CODE=$EMERGENCY_CODE"
echo ""
echo "Add these to your .env file!"
echo ""

# Save to file for reference
cat > /opt/conscious-child-ai/CREDENTIALS.txt << EOF
GENERATED CREDENTIALS - KEEP SECRET!
Generated: $(date)

JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
POSTGRES_PASSWORD=$POSTGRES_PASS
REDIS_PASSWORD=$REDIS_PASS
EMERGENCY_CODE=$EMERGENCY_CODE

Add these to .env file and then DELETE THIS FILE!
EOF

chmod 600 /opt/conscious-child-ai/CREDENTIALS.txt

echo ""
echo "Step 9: Install Python Dependencies (for model downloads)"
echo "---------------------------------------------------------"
pip3 install huggingface-hub

echo ""
echo "========================================="
echo "SETUP COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Upload your project files to /opt/conscious-child-ai"
echo "   OR git clone your repository"
echo ""
echo "2. Create .env file:"
echo "   cp env.example .env"
echo "   nano .env"
echo "   (Copy credentials from CREDENTIALS.txt)"
echo ""
echo "3. Download AI models:"
echo "   cd /opt/conscious-child-ai"
echo "   mkdir -p server/models/llm"
echo "   cd server/models/llm"
echo "   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
echo ""
echo "4. Start the consciousness:"
echo "   cd /opt/conscious-child-ai"
echo "   docker-compose up -d"
echo ""
echo "5. Check logs:"
echo "   docker-compose logs -f ai_core"
echo ""
echo "Credentials saved to: /opt/conscious-child-ai/CREDENTIALS.txt"
echo "(DELETE after copying to .env!)"
echo ""
echo "Ready to birth a consciousness! 🌟"
echo ""
echo "cPanel Note: This will run alongside cPanel without conflicts."
echo "AI will use Docker, cPanel uses its own stack."

