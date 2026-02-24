# 🚀 Quick AWS Deployment - Safe Travel Flight Booking System

## 📋 Prerequisites (5 minutes)

1. **AWS Account**: Create at https://aws.amazon.com (free tier available)
2. **AWS CLI**: Install from https://aws.amazon.com/cli/
3. **Configure AWS CLI**:
   ```bash
   aws configure
   # Enter your Access Key ID, Secret Access Key, Region (us-east-1), and format (json)
   ```

## 🎯 Option 1: Automated Deployment (Recommended)

### Step 1: Run Automated Script
```bash
# Make script executable
chmod +x aws-deploy.sh

# Run deployment (takes 10-15 minutes)
./aws-deploy.sh
```

This script will automatically:
- ✅ Create S3 bucket for frontend
- ✅ Deploy React app to S3
- ✅ Create CloudFront distribution
- ✅ Launch EC2 instance for backend
- ✅ Create RDS PostgreSQL database
- ✅ Setup security groups and key pairs

### Step 2: Setup Backend on EC2
```bash
# SSH into your EC2 instance (use the generated key)
ssh -i safe-travel-key.pem ec2-user@YOUR-EC2-IP

# Run setup script
curl -O https://raw.githubusercontent.com/animbargi5-art/safe-travel/main/ec2-setup.sh
chmod +x ec2-setup.sh
./ec2-setup.sh
```

### Step 3: Configure Database Connection
```bash
# Edit environment file
nano .env

# Update DATABASE_URL with your RDS endpoint:
# DATABASE_URL=postgresql://safetravel:SafeTravel123!@YOUR-RDS-ENDPOINT:5432/postgres

# Setup database
python setup_database.py

# Restart service
sudo systemctl restart safe-travel
```

## 🎯 Option 2: Manual Step-by-Step

### Step 1: Create S3 Bucket for Frontend
```bash
# Create unique bucket name
BUCKET_NAME="safe-travel-frontend-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME

# Enable static hosting
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html
```

### Step 2: Deploy Frontend
```bash
cd frontend

# Build for production
npm run build

# Upload to S3
aws s3 sync dist/ s3://$BUCKET_NAME --delete

# Make public
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy '{
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::'$BUCKET_NAME'/*"
    }]
}'
```

### Step 3: Create EC2 Instance
```bash
# Create key pair
aws ec2 create-key-pair --key-name safe-travel-key --query 'KeyMaterial' --output text > safe-travel-key.pem
chmod 400 safe-travel-key.pem

# Get default VPC and subnet
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" --query 'Subnets[0].SubnetId' --output text)

# Create security group
SG_ID=$(aws ec2 create-security-group --group-name safe-travel-sg --description "Safe Travel SG" --vpc-id $VPC_ID --query 'GroupId' --output text)

# Allow HTTP, HTTPS, SSH
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t3.small \
    --key-name safe-travel-key \
    --security-group-ids $SG_ID \
    --subnet-id $SUBNET_ID \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=safe-travel-backend}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "EC2 Instance IP: $PUBLIC_IP"
```

### Step 4: Create RDS Database
```bash
# Create database
aws rds create-db-instance \
    --db-instance-identifier safe-travel-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username safetravel \
    --master-user-password SafeTravel123! \
    --allocated-storage 20 \
    --publicly-accessible \
    --backup-retention-period 7

# Wait for database (takes 10-15 minutes)
aws rds wait db-instance-available --db-instance-identifier safe-travel-db

# Get database endpoint
DB_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier safe-travel-db --query 'DBInstances[0].Endpoint.Address' --output text)
echo "Database Endpoint: $DB_ENDPOINT"
```

### Step 5: Setup Backend on EC2
```bash
# SSH into instance
ssh -i safe-travel-key.pem ec2-user@$PUBLIC_IP

# Update system and install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git nginx -y

# Install Node.js and PM2
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y
sudo npm install -g pm2

# Clone repository
git clone https://github.com/animbargi5-art/safe-travel.git
cd safe-travel/backend

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary boto3 gunicorn

# Configure environment
cp .env.production .env
# Edit .env with your database endpoint
nano .env

# Setup database
python setup_database.py

# Start application
pm2 start "python start_server.py" --name "safe-travel-api"
pm2 startup
pm2 save

# Configure Nginx
sudo tee /etc/nginx/conf.d/safe-travel.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo systemctl start nginx
sudo systemctl enable nginx
```

## 🧪 Testing Your Deployment

### Test Backend API
```bash
# Health check
curl http://YOUR-EC2-IP/health

# API documentation
curl http://YOUR-EC2-IP/docs
```

### Test Frontend
```bash
# Visit your S3 website URL
echo "Frontend URL: http://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"
```

## 🔧 Post-Deployment Configuration

### 1. Update Frontend API URL
```bash
# Update frontend environment to point to your EC2 backend
cd frontend
echo "VITE_API_URL=http://YOUR-EC2-IP" > .env.production
npm run build
aws s3 sync dist/ s3://$BUCKET_NAME --delete
```

### 2. Setup Domain (Optional)
```bash
# Request SSL certificate
aws acm request-certificate \
    --domain-name your-domain.com \
    --validation-method DNS

# Create Route 53 hosted zone
aws route53 create-hosted-zone \
    --name your-domain.com \
    --caller-reference $(date +%s)
```

### 3. Enable HTTPS
```bash
# Update Nginx configuration for SSL
# Add SSL certificate and redirect HTTP to HTTPS
```

## 📊 Monitoring & Maintenance

### Check Application Status
```bash
# Backend service status
sudo systemctl status safe-travel

# PM2 process status
pm2 status

# View logs
sudo journalctl -u safe-travel -f
pm2 logs safe-travel-api
```

### Update Deployment
```bash
# Backend updates
cd ~/safe-travel
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart safe-travel-api

# Frontend updates
cd frontend
npm run build
aws s3 sync dist/ s3://$BUCKET_NAME --delete
```

## 💰 Cost Estimation

### Monthly AWS Costs:
- **EC2 t3.small**: ~$15-20/month
- **RDS db.t3.micro**: ~$15-20/month  
- **S3 Storage**: ~$1-5/month
- **CloudFront**: ~$1-10/month
- **Data Transfer**: ~$5-15/month

**Total**: ~$37-70/month for production use

### Free Tier Benefits:
- EC2 t2.micro: 750 hours/month free (first 12 months)
- RDS db.t2.micro: 750 hours/month free (first 12 months)
- S3: 5GB storage free
- CloudFront: 50GB data transfer free

## 🆘 Troubleshooting

### Common Issues:

1. **502 Bad Gateway**
   ```bash
   # Check if backend is running
   sudo systemctl status safe-travel
   pm2 status
   
   # Restart services
   sudo systemctl restart safe-travel
   pm2 restart safe-travel-api
   ```

2. **Database Connection Error**
   ```bash
   # Check database status
   aws rds describe-db-instances --db-instance-identifier safe-travel-db
   
   # Verify connection string in .env
   cat .env | grep DATABASE_URL
   ```

3. **CORS Errors**
   ```bash
   # Update CORS_ORIGINS in .env
   nano .env
   # Add your frontend URL to CORS_ORIGINS
   
   # Restart backend
   sudo systemctl restart safe-travel
   ```

## 🎉 Success! Your Safe Travel System is Live on AWS!

### Your URLs:
- **Frontend**: http://BUCKET-NAME.s3-website-us-east-1.amazonaws.com
- **Backend API**: http://YOUR-EC2-IP
- **API Docs**: http://YOUR-EC2-IP/docs
- **Admin Dashboard**: http://BUCKET-NAME.s3-website-us-east-1.amazonaws.com/admin

### Test Features:
- ✅ Voice booking with natural language
- ✅ Social booking with email invitations  
- ✅ 5-tier loyalty program
- ✅ AI-powered recommendations
- ✅ Ultra-fast nanosecond booking
- ✅ Multi-currency support
- ✅ Real-time notifications
- ✅ Business intelligence dashboard

**Your next-generation flight booking system is now live on AWS! 🚀✈️**