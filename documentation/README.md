# Terraform Infrastructure for Among Us MLOps Project

This directory contains Terraform configuration for deploying the Among Us MLOps project to AWS.

## 📋 Prerequisites

1. **Terraform** >= 1.0
   ```bash
   terraform --version
   ```

2. **AWS CLI** configured with appropriate credentials
   ```bash
   aws configure
   ```

3. **AWS Account** with permissions to create:
   - VPC, Subnets, Internet Gateway, NAT Gateway
   - S3, CloudFront
   - ECR, ECS (Fargate)
   - Application Load Balancer
   - CloudWatch Logs
   - IAM Roles and Policies

## 📁 File Structure

```
terraform/
├── provider.tf              # AWS provider configuration
├── variables.tf             # Variable definitions
├── outputs.tf               # Output values
├── terraform.tfvars         # Variable values (customize this)
├── vpc.tf                   # VPC, Subnets, Security Groups
├── s3.tf                    # S3 bucket, CloudFront
├── ecs.tf                   # ECR, ECS, Load Balancer, Auto Scaling
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Customize Configuration

Edit `terraform.tfvars` to match your requirements:

```hcl
aws_region     = "us-east-1"
environment    = "dev"  # or "staging", "prod"
# ... other variables
```

### 3. Plan Infrastructure

```bash
terraform plan -out=tfplan
```

Review the planned changes carefully.

### 4. Apply Infrastructure

```bash
terraform apply tfplan
```

This will create:
- VPC with public and private subnets
- S3 bucket for frontend with CloudFront distribution
- ECR repository for backend Docker images
- ECS cluster with Fargate tasks
- Application Load Balancer
- Auto Scaling policies
- CloudWatch Logs
- IAM roles and security groups

### 5. Get Outputs

```bash
terraform output
```

Important outputs:
- `ecr_repository_url` - Use for pushing Docker images
- `alb_dns_name` - Backend API endpoint
- `s3_frontend_bucket_name` - Frontend S3 bucket
- `cloudfront_domain_name` - CDN endpoint for frontend
- `github_actions_setup` - Environment variables for GitHub Actions

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                              │
└────────────────────┬──────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    ┌───▼────┐            ┌──────▼──────┐
    │ ALB    │            │ CloudFront  │
    │(Port80)│            │ (Frontend)  │
    └───┬────┘            └──────┬──────┘
        │                        │
    ┌───▼──────────────┐    ┌────▼──────┐
    │  ECS Cluster     │    │ S3 Bucket │
    │ (Fargate Tasks)  │    │(index.html)
    │                  │    │   assets  │
    │ ┌──────────────┐ │    └───────────┘
    │ │  Container   │ │
    │ │  :5000       │ │
    │ └──────────────┘ │
    │                  │
    └──────────────────┘
          │
     ECR Repository
    (Backend Image)
```

## 🔧 Configuration Options

### Environment-Specific Settings

For **development**:
```hcl
environment           = "dev"
ecs_desired_count     = 1
autoscaling_max_capacity = 2
log_retention_days    = 3
```

For **production**:
```hcl
environment           = "prod"
ecs_desired_count     = 2
autoscaling_max_capacity = 10
log_retention_days    = 30
enable_load_balancer  = true
```

### Container Resources

Available CPU/Memory combinations for Fargate:

| CPU | Memory Options |
|-----|-----------------|
| 256 | 512, 1024, 2048 |
| 512 | 1024-4096 (1024 increments) |
| 1024 | 2048-8192 (1024 increments) |
| 2048 | 4096-16384 (1024 increments) |
| 4096 | 8192-30720 (1024 increments) |

## 📝 Common Operations

### Push Docker Image to ECR

```bash
# Get ECR repository URL
ECR_URL=$(terraform output -raw ecr_repository_url)

# Build and push image
docker build -t $ECR_URL:latest .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL
docker push $ECR_URL:latest
```

### Update Container Configuration

1. Edit `terraform.tfvars`
2. Run `terraform plan`
3. Review changes
4. Run `terraform apply`

Example - Update desired task count:
```hcl
ecs_desired_count = 2
```

### Deploy Frontend to S3

```bash
# Get S3 bucket name
BUCKET=$(terraform output -raw s3_frontend_bucket_name)

# Upload files
aws s3 sync dist/ s3://$BUCKET/ --delete

# Get CloudFront distribution ID for cache invalidation
DIST_ID=$(terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

### Scale ECS Service

```hcl
# Manual scaling
ecs_desired_count = 3
terraform apply

# Auto-scaling configuration
enable_autoscaling        = true
autoscaling_min_capacity  = 1
autoscaling_max_capacity  = 5
autoscaling_target_cpu    = 70
```

### Monitor with CloudWatch

```bash
# Get log group name
LOG_GROUP=$(terraform output -raw cloudwatch_log_group_name)

# View logs
aws logs tail $LOG_GROUP --follow
```

## 🔐 Security Considerations

1. **S3 Bucket**: Public access is blocked; only CloudFront can access it
2. **ECS Security Group**: Only accepts traffic from ALB
3. **IAM Roles**: Principle of least privilege
4. **VPC**: Private subnets for ECS with NAT Gateway for egress
5. **ECR Scanning**: Enabled for vulnerability detection
6. **Encryption**: AES256 for S3; CloudWatch Logs encrypted by default

## 📊 Cost Optimization

1. **Use CloudFront Price Class 100** for lowest cost (covers 50% of edge locations)
2. **Enable Auto Scaling** to handle variable load
3. **Use Fargate Spot** for non-critical workloads
4. **Set Appropriate Log Retention** (7 days default)
5. **Monitor CloudWatch** for resource utilization

Estimated monthly cost (us-east-1, dev environment):
- ALB: ~$16
- ECS Fargate: ~$15-30 (1 task)
- S3: ~$1
- CloudFront: ~$0.50-5
- **Total: ~$30-50/month**

## 🛠️ Troubleshooting

### Terraform Plan Fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Validate Terraform syntax
terraform validate

# Format Terraform files
terraform fmt -recursive
```

### ECS Tasks Won't Start

```bash
# Check task definition
aws ecs describe-task-definition --task-definition among-us-mlops-task

# View CloudWatch logs
aws logs tail /ecs/among-us-mlops-task --follow
```

### Cannot Push to ECR

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Verify repository exists
aws ecr describe-repositories --repository-names among-us-mlops
```

## 🗑️ Cleanup

To destroy all infrastructure:

```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy infrastructure
terraform destroy
```

**⚠️ Warning**: This will delete all resources including S3 data. Back up important data first!

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform Best Practices](https://www.terraform.io/language)
- [AWS VPC Configuration](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [Fargate Pricing](https://aws.amazon.com/fargate/pricing/)

## 📧 Support

For issues or questions:
1. Check Terraform state: `terraform state list`
2. View resource details: `terraform state show <resource>`
3. Enable debug logging: `TF_LOG=DEBUG terraform apply`
