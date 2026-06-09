# Getting Started with Terraform

This guide will help you deploy the Among Us MLOps project to AWS using Terraform.

## 📋 Prerequisites

Before you start, ensure you have:

1. **AWS Account** - Create one at https://aws.amazon.com
2. **Terraform** - Install from https://www.terraform.io/downloads
3. **AWS CLI** - Install from https://aws.amazon.com/cli/
4. **AWS Credentials** - Configured with `aws configure`

Verify installation:
```bash
terraform version
aws --version
aws sts get-caller-identity
```

## 🚀 Deployment Steps

### Step 1: Navigate to Terraform Directory

```bash
cd terraform
```

### Step 2: Update Configuration (Optional)

Edit `terraform.tfvars` to customize your deployment:

```hcl
# Example: Change to production
environment = "prod"
ecs_desired_count = 2
enable_load_balancer = true
```

**Default values** are suitable for development. Don't change unless needed.

### Step 3: Initialize Terraform

```bash
terraform init
```

This downloads the AWS provider and initializes the Terraform working directory.

### Step 4: Review the Plan

```bash
terraform plan
```

This shows what resources will be created. Review carefully before proceeding.

### Step 5: Apply the Configuration

```bash
terraform apply
```

Type `yes` when prompted. This will create all AWS resources.

**⏱️ This may take 5-10 minutes.**

### Step 6: Retrieve Outputs

Once complete, retrieve the important outputs:

```bash
terraform output
```

Save these for later use:

```bash
terraform output -json > infrastructure-outputs.json
```

## 🐳 Deploy Backend Application

### Step 1: Build Docker Image

```bash
cd ..  # Go back to project root
docker build -t among-us-mlops:latest .
```

### Step 2: Get ECR Repository URL

```bash
cd terraform
ECR_URL=$(terraform output -raw ecr_repository_url)
echo $ECR_URL
```

### Step 3: Tag Image

```bash
docker tag among-us-mlops:latest $ECR_URL:latest
docker tag among-us-mlops:latest $ECR_URL:$(date +%Y%m%d-%H%M%S)
```

### Step 4: Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region $(terraform output -raw aws_region) | \
  docker login --username AWS --password-stdin $ECR_URL

# Push image
docker push $ECR_URL:latest
```

### Step 5: Verify Deployment

```bash
# Check ECS service
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ecs_service_name)

# View logs
aws logs tail $(terraform output -raw cloudwatch_log_group_name) --follow
```

## 📁 Deploy Frontend Application

### Step 1: Build Frontend

```bash
cd ..  # Go back to project root
mkdir -p dist
cp index.html dist/
cp -r assets dist/  # If assets directory exists
```

### Step 2: Upload to S3

```bash
cd terraform
S3_BUCKET=$(terraform output -raw s3_frontend_bucket_name)

aws s3 sync ../dist/ s3://$S3_BUCKET/ --delete
```

### Step 3: Invalidate CloudFront Cache (Optional)

```bash
DIST_ID=$(terraform output -raw cloudfront_distribution_id)

if [ ! -z "$DIST_ID" ]; then
  aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
fi
```

### Step 4: Access Application

- **Frontend**: 
  - S3: `http://$(terraform output -raw s3_frontend_bucket_url)`
  - CloudFront: `http://$(terraform output -raw cloudfront_domain_name)`

- **Backend API**:
  - ALB: `http://$(terraform output -raw alb_dns_name)`
  - Test: `curl http://$(terraform output -raw alb_dns_name):5000/model-info`

## 📊 Verify Everything Works

### Backend Health Check

```bash
ALB_DNS=$(terraform output -raw alb_dns_name)

# Check if service is running
curl http://$ALB_DNS/model-info

# Make a test prediction
curl -X POST http://$ALB_DNS/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Team": "Crewmate",
    "Task Completed": 5,
    "Imposter Kills": 0,
    "Game Length Sec": 300
  }'
```

### Frontend Health Check

```bash
FRONTEND_URL=$(terraform output -raw s3_frontend_bucket_url)

# Check if index.html is accessible
curl $FRONTEND_URL/index.html | head -20
```

### Infrastructure Status

```bash
# ECS Service Status
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ecs_service_name) \
  --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}'

# Check Auto Scaling
aws application-autoscaling describe-scalable-targets \
  --service-namespace ecs \
  --query 'ScalableTargets[?ResourceId==`service/among-us-mlops-cluster/among-us-mlops-service`]'
```

## 🔄 Making Changes

### Update Container Configuration

1. Edit `terraform.tfvars`
2. Run `terraform plan`
3. Review changes
4. Run `terraform apply`

Example:
```hcl
# Scale up
ecs_desired_count = 3

# Increase resources
container_cpu = 512
container_memory = 1024
```

### Update Docker Image

```bash
# Build new image
docker build -t $ECR_URL:latest .

# Push to ECR
docker push $ECR_URL:latest

# Force ECS to pull new image
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw ecs_service_name) \
  --force-new-deployment
```

### Update Frontend

```bash
# Build frontend
mkdir -p dist
cp index.html dist/
cp -r assets dist/

# Upload to S3
S3_BUCKET=$(terraform output -raw s3_frontend_bucket_name)
aws s3 sync dist/ s3://$S3_BUCKET/ --delete

# Invalidate cache
DIST_ID=$(terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

## 🧹 Cleanup

To destroy all infrastructure:

```bash
# Verify what will be deleted
terraform plan -destroy

# Delete everything
terraform destroy
```

**⚠️ Warning**: This will delete:
- ECS cluster and services
- ECR repository (and Docker images)
- S3 bucket and files
- ALB and target groups
- VPC and all subnets
- IAM roles and policies

Back up any important data first!

## 📚 Documentation

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS](https://docs.aws.amazon.com/ecs/)
- [AWS S3 Static Sites](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [AWS CloudFront](https://docs.aws.amazon.com/cloudfront/)

## ❓ Troubleshooting

### Error: No valid credential sources found
```bash
aws configure
aws sts get-caller-identity
```

### Error: Invalid provider configuration
```bash
# Check AWS region
aws configure get region

# Update terraform.tfvars
aws_region = "us-east-1"  # Change to your region
```

### ECS Tasks not starting
```bash
# View logs
aws logs tail /ecs/among-us-mlops-task --follow

# Check task definition
aws ecs describe-task-definition --task-definition among-us-mlops-task
```

### Docker push fails
```bash
# Verify ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# List ECR repositories
aws ecr describe-repositories
```

## 📞 Support

For additional help:
1. Check CloudWatch Logs: `aws logs tail /ecs/among-us-mlops-task --follow`
2. View Terraform state: `terraform state list`
3. Enable debug logging: `export TF_LOG=DEBUG && terraform plan`
