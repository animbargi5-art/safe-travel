#!/bin/bash

# 🚀 Safe Travel AWS Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting Safe Travel AWS Deployment..."
echo "================================================"

# Configuration
REGION="us-east-1"
BUCKET_NAME="safe-travel-frontend-$(date +%s)"
DB_NAME="safe-travel-db"
EC2_KEY_NAME="safe-travel-key"
INSTANCE_TYPE="t3.small"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if AWS CLI is installed and configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Run 'aws configure' first."
        exit 1
    fi
    
    print_status "AWS CLI is configured"
}

# Create S3 bucket for frontend
create_s3_bucket() {
    echo "📦 Creating S3 bucket for frontend..."
    
    aws s3 mb s3://$BUCKET_NAME --region $REGION
    
    # Enable static website hosting
    aws s3 website s3://$BUCKET_NAME \
        --index-document index.html \
        --error-document index.html
    
    # Set bucket policy for public read
    cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket $BUCKET_NAME \
        --policy file://bucket-policy.json
    
    rm bucket-policy.json
    
    print_status "S3 bucket created: $BUCKET_NAME"
}

# Build and upload frontend
deploy_frontend() {
    echo "🌐 Building and deploying frontend..."
    
    cd frontend
    
    # Create production environment file
    echo "VITE_API_URL=https://api.your-domain.com" > .env.production
    
    # Build for production
    npm run build
    
    # Upload to S3
    aws s3 sync dist/ s3://$BUCKET_NAME --delete
    
    cd ..
    
    print_status "Frontend deployed to S3"
    echo "Frontend URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
}

# Create CloudFront distribution
create_cloudfront() {
    echo "🌍 Creating CloudFront distribution..."
    
    cat > cloudfront-config.json << EOF
{
    "CallerReference": "safe-travel-$(date +%s)",
    "Comment": "Safe Travel Frontend Distribution",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
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
        "MinTTL": 0,
        "Compress": true
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
}
EOF
    
    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file://cloudfront-config.json \
        --query 'Distribution.Id' \
        --output text)
    
    rm cloudfront-config.json
    
    print_status "CloudFront distribution created: $DISTRIBUTION_ID"
    print_warning "CloudFront deployment takes 15-20 minutes to complete"
}

# Create security group
create_security_group() {
    echo "🔒 Creating security group..."
    
    # Get default VPC ID
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=isDefault,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    # Create security group
    SG_ID=$(aws ec2 create-security-group \
        --group-name safe-travel-sg \
        --description "Safe Travel Security Group" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)
    
    # Allow SSH (port 22)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    
    # Allow HTTP (port 80)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0
    
    # Allow HTTPS (port 443)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0
    
    # Allow backend port (8000)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0
    
    print_status "Security group created: $SG_ID"
    echo $SG_ID > security-group-id.txt
}

# Create key pair
create_key_pair() {
    echo "🔑 Creating EC2 key pair..."
    
    aws ec2 create-key-pair \
        --key-name $EC2_KEY_NAME \
        --query 'KeyMaterial' \
        --output text > $EC2_KEY_NAME.pem
    
    chmod 400 $EC2_KEY_NAME.pem
    
    print_status "Key pair created: $EC2_KEY_NAME.pem"
    print_warning "Keep this key file safe! You'll need it to access your EC2 instance"
}

# Launch EC2 instance
launch_ec2() {
    echo "🖥️  Launching EC2 instance..."
    
    # Get latest Amazon Linux 2 AMI ID
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text)
    
    # Get default subnet
    SUBNET_ID=$(aws ec2 describe-subnets \
        --filters "Name=default-for-az,Values=true" \
        --query 'Subnets[0].SubnetId' \
        --output text)
    
    # Get security group ID
    SG_ID=$(cat security-group-id.txt)
    
    # Launch instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $EC2_KEY_NAME \
        --security-group-ids $SG_ID \
        --subnet-id $SUBNET_ID \
        --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=safe-travel-backend}]' \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    print_status "EC2 instance launched: $INSTANCE_ID"
    echo $INSTANCE_ID > instance-id.txt
    
    # Wait for instance to be running
    echo "⏳ Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    print_status "Instance is running at: $PUBLIC_IP"
    echo $PUBLIC_IP > public-ip.txt
}

# Create RDS database
create_database() {
    echo "🗄️  Creating RDS PostgreSQL database..."
    
    # Create DB subnet group
    aws rds create-db-subnet-group \
        --db-subnet-group-name safe-travel-subnet-group \
        --db-subnet-group-description "Safe Travel DB Subnet Group" \
        --subnet-ids $(aws ec2 describe-subnets --query 'Subnets[0:2].SubnetId' --output text)
    
    # Create database
    aws rds create-db-instance \
        --db-instance-identifier $DB_NAME \
        --db-instance-class db.t3.micro \
        --engine postgres \
        --master-username safetravel \
        --master-user-password SafeTravel123! \
        --allocated-storage 20 \
        --db-subnet-group-name safe-travel-subnet-group \
        --backup-retention-period 7 \
        --storage-encrypted \
        --publicly-accessible
    
    print_status "Database creation initiated: $DB_NAME"
    print_warning "Database creation takes 10-15 minutes to complete"
}

# Generate deployment summary
generate_summary() {
    echo ""
    echo "🎉 Deployment Summary"
    echo "================================================"
    echo "Frontend S3 Bucket: $BUCKET_NAME"
    echo "Frontend URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
    echo "EC2 Instance: $(cat instance-id.txt)"
    echo "Public IP: $(cat public-ip.txt)"
    echo "SSH Command: ssh -i $EC2_KEY_NAME.pem ec2-user@$(cat public-ip.txt)"
    echo "Database: $DB_NAME"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Wait for database to be available (10-15 minutes)"
    echo "2. SSH into EC2 instance and setup backend"
    echo "3. Configure domain and SSL certificate"
    echo "4. Test all features"
    echo ""
    echo "📖 Full setup instructions in AWS_DEPLOYMENT_GUIDE.md"
}

# Main deployment flow
main() {
    check_aws_cli
    create_security_group
    create_key_pair
    create_s3_bucket
    deploy_frontend
    create_cloudfront
    launch_ec2
    create_database
    generate_summary
}

# Run main function
main

print_status "AWS deployment initiated successfully! 🚀"