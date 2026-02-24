# 🚀 Safe Travel AWS Deployment Script (PowerShell Version)
# This script automates the deployment process for Windows

param(
    [string]$Region = "us-east-1",
    [string]$InstanceType = "t3.small"
)

# Configuration
$BucketName = "safe-travel-frontend-$(Get-Date -Format 'yyyyMMddHHmmss')"
$DBName = "safe-travel-db"
$KeyName = "safe-travel-key"

Write-Host "🚀 Starting Safe Travel AWS Deployment..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Yellow

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Check if AWS CLI is configured
function Test-AWSConfiguration {
    try {
        $identity = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "AWS CLI is configured"
            return $true
        }
    }
    catch {
        Write-Error "AWS CLI is not configured. Run 'aws configure' first."
        return $false
    }
    return $false
}

# Create S3 bucket for frontend
function New-S3Bucket {
    Write-Host "📦 Creating S3 bucket for frontend..." -ForegroundColor Cyan
    
    try {
        aws s3 mb "s3://$BucketName" --region $Region
        
        # Enable static website hosting
        aws s3 website "s3://$BucketName" --index-document index.html --error-document index.html
        
        # Create bucket policy
        $bucketPolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BucketName/*"
        }
    ]
}
"@
        
        $bucketPolicy | Out-File -FilePath "bucket-policy.json" -Encoding UTF8
        aws s3api put-bucket-policy --bucket $BucketName --policy file://bucket-policy.json
        Remove-Item "bucket-policy.json"
        
        Write-Status "S3 bucket created: $BucketName"
        return $BucketName
    }
    catch {
        Write-Error "Failed to create S3 bucket: $_"
        return $null
    }
}

# Build and deploy frontend
function Deploy-Frontend {
    param([string]$Bucket)
    
    Write-Host "🌐 Building and deploying frontend..." -ForegroundColor Cyan
    
    try {
        Set-Location "frontend"
        
        # Create production environment file
        "VITE_API_URL=https://api.your-domain.com" | Out-File -FilePath ".env.production" -Encoding UTF8
        
        # Build for production
        npm run build
        
        # Upload to S3
        aws s3 sync dist/ "s3://$Bucket" --delete
        
        Set-Location ".."
        
        Write-Status "Frontend deployed to S3"
        $frontendUrl = "http://$Bucket.s3-website-$Region.amazonaws.com"
        Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Yellow
        return $frontendUrl
    }
    catch {
        Write-Error "Failed to deploy frontend: $_"
        Set-Location ".."
        return $null
    }
}

# Create security group
function New-SecurityGroup {
    Write-Host "🔒 Creating security group..." -ForegroundColor Cyan
    
    try {
        # Get default VPC ID
        $vpcId = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text
        
        # Create security group
        $sgId = aws ec2 create-security-group --group-name "safe-travel-sg" --description "Safe Travel Security Group" --vpc-id $vpcId --query 'GroupId' --output text
        
        # Allow SSH (port 22)
        aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 22 --cidr 0.0.0.0/0
        
        # Allow HTTP (port 80)
        aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 80 --cidr 0.0.0.0/0
        
        # Allow HTTPS (port 443)
        aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 443 --cidr 0.0.0.0/0
        
        # Allow backend port (8000)
        aws ec2 authorize-security-group-ingress --group-id $sgId --protocol tcp --port 8000 --cidr 0.0.0.0/0
        
        Write-Status "Security group created: $sgId"
        $sgId | Out-File -FilePath "security-group-id.txt" -Encoding UTF8
        return $sgId
    }
    catch {
        Write-Error "Failed to create security group: $_"
        return $null
    }
}

# Create key pair
function New-KeyPair {
    Write-Host "🔑 Creating EC2 key pair..." -ForegroundColor Cyan
    
    try {
        aws ec2 create-key-pair --key-name $KeyName --query 'KeyMaterial' --output text | Out-File -FilePath "$KeyName.pem" -Encoding UTF8
        
        Write-Status "Key pair created: $KeyName.pem"
        Write-Warning "Keep this key file safe! You'll need it to access your EC2 instance"
        return $KeyName
    }
    catch {
        Write-Error "Failed to create key pair: $_"
        return $null
    }
}

# Launch EC2 instance
function New-EC2Instance {
    param([string]$SecurityGroupId)
    
    Write-Host "🖥️  Launching EC2 instance..." -ForegroundColor Cyan
    
    try {
        # Get latest Amazon Linux 2 AMI ID
        $amiId = aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' --output text
        
        # Get default subnet
        $subnetId = aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" --query 'Subnets[0].SubnetId' --output text
        
        # Launch instance
        $instanceId = aws ec2 run-instances --image-id $amiId --count 1 --instance-type $InstanceType --key-name $KeyName --security-group-ids $SecurityGroupId --subnet-id $subnetId --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=safe-travel-backend}]' --query 'Instances[0].InstanceId' --output text
        
        Write-Status "EC2 instance launched: $instanceId"
        $instanceId | Out-File -FilePath "instance-id.txt" -Encoding UTF8
        
        # Wait for instance to be running
        Write-Host "⏳ Waiting for instance to be running..." -ForegroundColor Yellow
        aws ec2 wait instance-running --instance-ids $instanceId
        
        # Get public IP
        $publicIp = aws ec2 describe-instances --instance-ids $instanceId --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
        
        Write-Status "Instance is running at: $publicIp"
        $publicIp | Out-File -FilePath "public-ip.txt" -Encoding UTF8
        return @{
            InstanceId = $instanceId
            PublicIp = $publicIp
        }
    }
    catch {
        Write-Error "Failed to launch EC2 instance: $_"
        return $null
    }
}

# Create RDS database
function New-RDSDatabase {
    Write-Host "🗄️  Creating RDS PostgreSQL database..." -ForegroundColor Cyan
    
    try {
        # Get subnets for DB subnet group
        $subnets = aws ec2 describe-subnets --query 'Subnets[0:2].SubnetId' --output text
        $subnetArray = $subnets -split "`t"
        
        # Create DB subnet group
        aws rds create-db-subnet-group --db-subnet-group-name "safe-travel-subnet-group" --db-subnet-group-description "Safe Travel DB Subnet Group" --subnet-ids $subnetArray[0] $subnetArray[1]
        
        # Create database
        aws rds create-db-instance --db-instance-identifier $DBName --db-instance-class "db.t3.micro" --engine postgres --master-username safetravel --master-user-password "SafeTravel123!" --allocated-storage 20 --db-subnet-group-name "safe-travel-subnet-group" --backup-retention-period 7 --storage-encrypted --publicly-accessible
        
        Write-Status "Database creation initiated: $DBName"
        Write-Warning "Database creation takes 10-15 minutes to complete"
        return $DBName
    }
    catch {
        Write-Error "Failed to create database: $_"
        return $null
    }
}

# Generate deployment summary
function Show-DeploymentSummary {
    param(
        [string]$BucketName,
        [string]$FrontendUrl,
        [hashtable]$EC2Info,
        [string]$DatabaseName
    )
    
    Write-Host ""
    Write-Host "🎉 Deployment Summary" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Yellow
    Write-Host "Frontend S3 Bucket: $BucketName" -ForegroundColor White
    Write-Host "Frontend URL: $FrontendUrl" -ForegroundColor White
    Write-Host "EC2 Instance: $($EC2Info.InstanceId)" -ForegroundColor White
    Write-Host "Public IP: $($EC2Info.PublicIp)" -ForegroundColor White
    Write-Host "SSH Command: ssh -i $KeyName.pem ec2-user@$($EC2Info.PublicIp)" -ForegroundColor White
    Write-Host "Database: $DatabaseName" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Wait for database to be available (10-15 minutes)" -ForegroundColor White
    Write-Host "2. SSH into EC2 instance and setup backend" -ForegroundColor White
    Write-Host "3. Configure domain and SSL certificate" -ForegroundColor White
    Write-Host "4. Test all features" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 Full setup instructions in AWS_DEPLOYMENT_GUIDE.md" -ForegroundColor White
}

# Main deployment function
function Start-Deployment {
    Write-Host "🚀 Starting Safe Travel AWS Deployment..." -ForegroundColor Green
    
    # Check AWS configuration
    if (-not (Test-AWSConfiguration)) {
        Write-Error "Please configure AWS CLI first with 'aws configure'"
        return
    }
    
    try {
        # Create infrastructure
        $bucket = New-S3Bucket
        if (-not $bucket) { throw "Failed to create S3 bucket" }
        
        $frontendUrl = Deploy-Frontend -Bucket $bucket
        if (-not $frontendUrl) { throw "Failed to deploy frontend" }
        
        $securityGroup = New-SecurityGroup
        if (-not $securityGroup) { throw "Failed to create security group" }
        
        $keyPair = New-KeyPair
        if (-not $keyPair) { throw "Failed to create key pair" }
        
        $ec2Info = New-EC2Instance -SecurityGroupId $securityGroup
        if (-not $ec2Info) { throw "Failed to launch EC2 instance" }
        
        $database = New-RDSDatabase
        if (-not $database) { throw "Failed to create database" }
        
        # Show summary
        Show-DeploymentSummary -BucketName $bucket -FrontendUrl $frontendUrl -EC2Info $ec2Info -DatabaseName $database
        
        Write-Status "AWS deployment initiated successfully! 🚀"
    }
    catch {
        Write-Error "Deployment failed: $_"
    }
}

# Run the deployment
Start-Deployment