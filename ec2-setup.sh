#!/bin/bash

# 🖥️ EC2 Instance Setup Script for Safe Travel Backend
# Run this script on your EC2 instance after SSH connection

set -e

echo "🚀 Setting up Safe Travel Backend on EC2..."
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Update system
echo "📦 Updating system packages..."
sudo yum update -y
print_status "System updated"

# Install Python 3.9+
echo "🐍 Installing Python..."
sudo yum install python3 python3-pip git -y
print_status "Python installed"

# Install Node.js (for any build tools)
echo "📦 Installing Node.js..."
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y
print_status "Node.js installed"

# Install Nginx
echo "🌐 Installing Nginx..."
sudo yum install nginx -y
sudo systemctl enable nginx
print_status "Nginx installed"

# Install PM2 for process management
echo "⚙️ Installing PM2..."
sudo npm install -g pm2
print_status "PM2 installed"

# Clone repository
echo "📥 Cloning Safe Travel repository..."
if [ ! -d "safe-travel" ]; then
    git clone https://github.com/animbargi5-art/safe-travel.git
else
    cd safe-travel && git pull origin main && cd ..
fi
print_status "Repository cloned/updated"

# Setup backend
echo "🔧 Setting up backend..."
cd safe-travel/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-aws.txt

print_status "Backend dependencies installed"

# Setup environment variables
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.production .env
    print_warning "Please edit .env file with your actual database URL and secrets"
fi

# Setup database (will need to update DATABASE_URL first)
echo "🗄️ Setting up database..."
print_warning "Make sure to update DATABASE_URL in .env before running this"
read -p "Have you updated the DATABASE_URL in .env? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python setup_database.py
    print_status "Database setup completed"
else
    print_warning "Skipping database setup. Run 'python setup_database.py' after updating .env"
fi

# Create systemd service for the backend
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/safe-travel.service > /dev/null << EOF
[Unit]
Description=Safe Travel Flight Booking API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/safe-travel/backend
Environment=PATH=/home/ec2-user/safe-travel/backend/venv/bin
ExecStart=/home/ec2-user/safe-travel/backend/venv/bin/python start_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable safe-travel
sudo systemctl start safe-travel

print_status "Safe Travel service created and started"

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/conf.d/safe-travel.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain

    # API routes
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization";
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 200;
        }
    }

    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Test and start Nginx
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx

print_status "Nginx configured and started"

# Setup PM2 (alternative to systemd)
echo "⚙️ Setting up PM2 as backup process manager..."
pm2 start "python start_server.py" --name "safe-travel-api" --interpreter python3
pm2 startup
pm2 save

print_status "PM2 configured"

# Create deployment script
echo "📝 Creating deployment script..."
tee ~/deploy-backend.sh > /dev/null << 'EOF'
#!/bin/bash
echo "🚀 Deploying Safe Travel Backend..."

cd ~/safe-travel
git pull origin main

cd backend
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-aws.txt

# Restart services
sudo systemctl restart safe-travel
pm2 restart safe-travel-api

echo "✅ Backend deployment complete!"
EOF

chmod +x ~/deploy-backend.sh

print_status "Deployment script created at ~/deploy-backend.sh"

# Get instance information
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "🎉 EC2 Setup Complete!"
echo "======================"
echo "Backend API: http://$INSTANCE_IP"
echo "Health Check: http://$INSTANCE_IP/health"
echo "API Docs: http://$INSTANCE_IP/docs"
echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with correct DATABASE_URL"
echo "2. Run: python setup_database.py (if not done already)"
echo "3. Test API: curl http://$INSTANCE_IP/health"
echo "4. Configure domain and SSL certificate"
echo ""
echo "🔧 Useful Commands:"
echo "- Check service status: sudo systemctl status safe-travel"
echo "- View logs: sudo journalctl -u safe-travel -f"
echo "- Restart service: sudo systemctl restart safe-travel"
echo "- Deploy updates: ~/deploy-backend.sh"

print_status "Setup completed successfully! 🚀"