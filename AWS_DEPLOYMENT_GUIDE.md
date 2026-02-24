# 🚀 AWS Deployment Guide - Safe Travel Flight Booking System

## 📋 Overview
We'll deploy using AWS services for maximum scalability and reliability:
- **Frontend**: AWS S3 + CloudFront (Static hosting)
- **Backend**: AWS EC2 + Application Load Balancer
- **Database**: AWS RDS (PostgreSQL) 
- **Domain**: Route 53 (Optional)
- **SSL**: AWS Certificate Manager

## 💰 Estimated Monthly Cost
- **Development**: $15-25/month
- **Production**: $50-100/month (depending on traffic)

---

## 🎯 Step 1: AWS Account Setup

### 1.1 Create AWS Account
1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Follow the registration process
4. **Important**: Set up billing alerts to avoid unexpected charges

### 1.2 Install AWS CLI
```bash
# Download and install AWS CLI v2
# Windows: Download from https://aws.amazon.com/cli/
# Or use pip:
pip install awscli

# Verify installation
aws --version
```

### 1.3 Configure AWS CLI
```bash
# Configure with your credentials
aws configure

# Enter when prompted:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1
# Default output format: json
```

---

## 🗄️ Step 2: Database Setup (RDS PostgreSQL)

### 2.1 Create RDS Instance
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name safe-travel-subnet-group \
    --db-subnet-group-description "Safe Travel DB Subnet Group" \
    --subnet-ids subnet-12345678 subnet-87654321

# Create PostgreSQL database
aws rds create-db-instance \
    --db-instance-identifier safe-travel-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username safetravel \
    --master-user-password YourSecurePassword123! \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name safe-travel-subnet-group \
    --backup-retention-period 7 \
    --storage-encrypted
```

### 2.2 Update Backend for PostgreSQL
Create `backend/requirements-aws.txt`:
```
# All existing requirements plus:
psycopg2-binary==2.9.11
boto3==1.34.0
python-dotenv==1.0.0
```

Update `backend/.env.production`:
```bash
DATABASE_URL=postgresql://safetravel:YourSecurePassword123!@safe-travel-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres
SECRET_KEY=your-super-secret-production-key-here
ENVIRONMENT=production
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

---

## 🖥️ Step 3: Backend Deployment (EC2)

### 3.1 Create EC2 Instance
```bash
# Create key pair for SSH access
aws ec2 create-key-pair \
    --key-name safe-travel-key \
    --query 'KeyMaterial' \
    --output text > safe-travel-key.pem

# Set permissions
chmod 400 safe-travel-key.pem

# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t3.small \
    --key-name safe-travel-key \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=safe-travel-backend}]'
```

### 3.2 Setup EC2 Instance
```bash
# SSH into your instance
ssh -i safe-travel-key.pem ec2-user@your-ec2-public-ip

# Update system
sudo yum update -y

# Install Python 3.9+
sudo yum install python3 python3-pip git -y

# Install Node.js (for any build tools)
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y

# Install Nginx
sudo yum install nginx -y

# Install PM2 for process management
sudo npm install -g pm2

# Clone your repository
git clone https://github.com/animbargi5-art/safe-travel.git
cd safe-travel/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-aws.txt

# Setup environment
cp .env.production .env

# Setup database
python setup_database.py

# Start application with PM2
pm2 start "python start_server.py" --name "safe-travel-api"
pm2 startup
pm2 save
```

### 3.3 Configure Nginx
Create `/etc/nginx/conf.d/safe-travel.conf`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

```bash
# Test and restart Nginx
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 🌐 Step 4: Frontend Deployment (S3 + CloudFront)

### 4.1 Prepare Frontend for Production
```bash
# In your local frontend directory
cd frontend

# Update environment for production
echo "VITE_API_URL=https://api.your-domain.com" > .env.production

# Build for production
npm run build
```

### 4.2 Create S3 Bucket
```bash
# Create S3 bucket for static hosting
aws s3 mb s3://safe-travel-frontend-bucket

# Enable static website hosting
aws s3 website s3://safe-travel-frontend-bucket \
    --index-document index.html \
    --error-document index.html

# Upload build files
aws s3 sync dist/ s3://safe-travel-frontend-bucket --delete

# Set public read policy
aws s3api put-bucket-policy \
    --bucket safe-travel-frontend-bucket \
    --policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::safe-travel-frontend-bucket/*"
            }
        ]
    }'
```

### 4.3 Setup CloudFront Distribution
```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --distribution-config '{
        "CallerReference": "safe-travel-'$(date +%s)'",
        "Comment": "Safe Travel Frontend Distribution",
        "DefaultRootObject": "index.html",
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "S3-safe-travel-frontend-bucket",
                    "DomainName": "safe-travel-frontend-bucket.s3.amazonaws.com",
                    "S3OriginConfig": {
                        "OriginAccessIdentity": ""
                    }
                }
            ]
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "S3-safe-travel-frontend-bucket",
            "ViewerProtocolPolicy": "redirect-to-https",
            "TrustedSigners": {
                "Enabled": false,
                "Quantity": 0
            },
            "ForwardedValues": {
                "QueryString": false,
                "Cookies": {
                    "Forward": "none"
                }
            },
            "MinTTL": 0
        },
        "Enabled": true,
        "PriceClass": "PriceClass_100"
    }'
```

---

## 🔒 Step 5: SSL Certificate & Domain Setup

### 5.1 Request SSL Certificate
```bash
# Request certificate (replace with your domain)
aws acm request-certificate \
    --domain-name your-domain.com \
    --subject-alternative-names www.your-domain.com \
    --validation-method DNS \
    --region us-east-1
```

### 5.2 Setup Route 53 (Optional)
```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name your-domain.com \
    --caller-reference safe-travel-$(date +%s)

# Create A record for backend
aws route53 change-resource-record-sets \
    --hosted-zone-id Z123456789 \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "api.your-domain.com",
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [
                        {
                            "Value": "YOUR-EC2-PUBLIC-IP"
                        }
                    ]
                }
            }
        ]
    }'
```

---

## 🔧 Step 6: Application Load Balancer (Optional - for High Availability)

### 6.1 Create Application Load Balancer
```bash
# Create target group
aws elbv2 create-target-group \
    --name safe-travel-targets \
    --protocol HTTP \
    --port 8000 \
    --vpc-id vpc-12345678 \
    --health-check-path /health

# Create load balancer
aws elbv2 create-load-balancer \
    --name safe-travel-alb \
    --subnets subnet-12345678 subnet-87654321 \
    --security-groups sg-12345678

# Register EC2 instance with target group
aws elbv2 register-targets \
    --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789:targetgroup/safe-travel-targets/1234567890123456 \
    --targets Id=i-1234567890abcdef0
```

---

## 📊 Step 7: Monitoring & Logging

### 7.1 CloudWatch Setup
```bash
# Install CloudWatch agent on EC2
sudo yum install amazon-cloudwatch-agent -y

# Configure CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### 7.2 Setup Alarms
```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "safe-travel-high-cpu" \
    --alarm-description "Alarm when CPU exceeds 70%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 70 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 2
```

---

## 🚀 Step 8: Deployment Automation

### 8.1 Create Deployment Script
Create `deploy-aws.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying Safe Travel to AWS..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build

# Upload to S3
echo "☁️ Uploading to S3..."
aws s3 sync dist/ s3://safe-travel-frontend-bucket --delete

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id E1234567890123 \
    --paths "/*"

# Deploy backend
echo "🖥️ Deploying backend..."
ssh -i safe-travel-key.pem ec2-user@your-ec2-ip << 'EOF'
cd safe-travel
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart safe-travel-api
EOF

echo "✅ Deployment complete!"
echo "🌐 Frontend: https://your-cloudfront-domain.cloudfront.net"
echo "🔗 Backend: https://api.your-domain.com"
```

### 8.2 Make Script Executable
```bash
chmod +x deploy-aws.sh
```

---

## 🔐 Step 9: Security Best Practices

### 9.1 Security Groups
```bash
# Backend security group (allow HTTP/HTTPS and SSH)
aws ec2 create-security-group \
    --group-name safe-travel-backend-sg \
    --description "Safe Travel Backend Security Group"

# Allow SSH (port 22)
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

### 9.2 Environment Variables Security
```bash
# Use AWS Systems Manager Parameter Store
aws ssm put-parameter \
    --name "/safe-travel/database-url" \
    --value "postgresql://..." \
    --type "SecureString"

aws ssm put-parameter \
    --name "/safe-travel/secret-key" \
    --value "your-secret-key" \
    --type "SecureString"
```

---

## 📋 Step 10: Final Checklist

### ✅ Pre-Deployment Checklist
- [ ] AWS account created and configured
- [ ] Domain name purchased (optional)
- [ ] SSL certificate requested and validated
- [ ] Database created and accessible
- [ ] EC2 instance launched and configured
- [ ] S3 bucket created for frontend
- [ ] CloudFront distribution created
- [ ] Security groups configured
- [ ] Environment variables set

### ✅ Post-Deployment Testing
- [ ] Frontend loads correctly
- [ ] Backend API responds to health checks
- [ ] Database connections working
- [ ] Authentication flow works
- [ ] Voice booking feature functional
- [ ] Social booking emails sending
- [ ] Loyalty program calculating points
- [ ] WebSocket connections established
- [ ] SSL certificate valid
- [ ] Performance monitoring active

---

## 🎯 Quick Start Commands

```bash
# 1. Setup AWS CLI
aws configure

# 2. Create database
aws rds create-db-instance --db-instance-identifier safe-travel-db ...

# 3. Launch EC2
aws ec2 run-instances --image-id ami-0c02fb55956c7d316 ...

# 4. Create S3 bucket
aws s3 mb s3://safe-travel-frontend-bucket

# 5. Deploy frontend
npm run build && aws s3 sync dist/ s3://safe-travel-frontend-bucket

# 6. Setup backend on EC2
ssh -i safe-travel-key.pem ec2-user@your-ec2-ip
```

---

## 💰 Cost Optimization Tips

1. **Use t3.micro for development** (free tier eligible)
2. **Enable auto-scaling** for production traffic
3. **Use CloudFront caching** to reduce S3 costs
4. **Set up billing alerts** to monitor spending
5. **Use Reserved Instances** for long-term savings

---

## 🆘 Troubleshooting

### Common Issues:
1. **502 Bad Gateway**: Check if backend service is running
2. **CORS errors**: Verify CORS_ORIGINS in environment
3. **Database connection**: Check security groups and credentials
4. **SSL issues**: Ensure certificate is validated and attached

### Useful Commands:
```bash
# Check EC2 instance status
aws ec2 describe-instances --instance-ids i-1234567890abcdef0

# Check RDS status
aws rds describe-db-instances --db-instance-identifier safe-travel-db

# View CloudFront distributions
aws cloudfront list-distributions

# Check S3 bucket contents
aws s3 ls s3://safe-travel-frontend-bucket
```

---

**🎉 Your Safe Travel Flight Booking System will be live on AWS!**

**Estimated URLs after deployment:**
- **Frontend**: https://your-cloudfront-domain.cloudfront.net
- **Backend API**: https://api.your-domain.com
- **Admin Dashboard**: https://your-cloudfront-domain.cloudfront.net/admin

**Ready to deploy? Let's start with Step 1! 🚀**