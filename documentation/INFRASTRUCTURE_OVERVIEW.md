# 🚀 Among Us MLOps - Complete Terraform Infrastructure

## 📦 Project Overview

Complete Terraform Infrastructure-as-Code for deploying the Among Us MLOps project to AWS with:

- **Frontend**: Deployed to S3 with optional CloudFront CDN
- **Backend**: Containerized with Docker, deployed to ECS Fargate
- **Network**: Full VPC setup with public/private subnets
- **Load Balancing**: Application Load Balancer for backend
- **Auto Scaling**: ECS service auto-scaling based on CPU/Memory
- **Logging**: CloudWatch Logs for monitoring
- **Registry**: ECR for Docker image storage

## 📋 Files Structure

```
terraform/
├── provider.tf              # AWS provider configuration
├── variables.tf             # All variable definitions (100+ lines)
├── outputs.tf               # Output values (30+ resources)
├── vpc.tf                   # VPC, Subnets, Security Groups (200 lines)
├── s3.tf                    # S3 Bucket, CloudFront (150 lines)
├── ecs.tf                   # ECR, ECS, ALB, Auto Scaling (400+ lines)
├── terraform.tfvars         # Default variable values (customizable)
│
├── README.md                # Comprehensive Terraform guide
├── GETTING_STARTED.md       # Step-by-step deployment guide
├── QUICK_REFERENCE.md       # Common commands and troubleshooting
├── setup.sh                 # Automated setup script
└── .gitignore               # Git ignore rules
```

## 🏗️ Infrastructure Provisioned

### Networking (VPC)
- 1 VPC with CIDR block 10.0.0.0/16
- 2 Public Subnets (10.0.101.0/24, 10.0.102.0/24)
- 2 Private Subnets (10.0.1.0/24, 10.0.2.0/24)
- Internet Gateway
- 2 NAT Gateways (for private subnet internet access)
- Route tables (public & private)
- 2 Security Groups (ALB & ECS)

### Frontend (S3 + CloudFront)
- S3 bucket with website configuration
- Public access blocked (bucket policies)
- Versioning enabled
- AES256 encryption
- CloudFront distribution with OAI
- Custom cache behaviors for index.html

### Backend Container Registry (ECR)
- ECR repository for Docker images
- Image scanning on push enabled
- Lifecycle policy (keep last 10 images, remove untagged after 7 days)
- AES256 encryption

### Backend Compute (ECS)
- ECS Cluster (Fargate capacity providers)
- ECS Task Definition (Python/Flask application)
- ECS Service with:
  - Load balancer integration
  - CloudWatch logging
  - Health checks
  - Deployment circuit breaker
- CloudWatch Log Group (/ecs/among-us-mlops-task)

### Load Balancing
- Application Load Balancer (ALB)
- Target Group (health checks on /model-info)
- Listener (port 80)
- Security group allowing inbound port 80

### Auto Scaling
- Application Auto Scaling target
- CPU-based scaling policy (target: 70%)
- Memory-based scaling policy (target: 80%)
- Min 1 / Max 3 tasks (configurable)

### IAM
- ECS Task Execution Role
- ECS Task Role
- S3 access policies
- CloudWatch Logs permissions

## 🚀 Quick Start

### 1. Initialize Infrastructure

```bash
cd terraform
terraform init
terraform validate
```

### 2. Review Configuration

```bash
# View variables
cat terraform.tfvars

# Show plan
terraform plan
```

### 3. Deploy Infrastructure

```bash
terraform apply
```

### 4. Get Outputs

```bash
terraform output
# or save to file
terraform output -json > infrastructure.json
```

### 5. Deploy Application

```bash
# Build Docker image
docker build -t among-us-mlops:latest ..

# Get ECR URL
ECR_URL=$(terraform output -raw ecr_repository_url)

# Push to ECR
docker tag among-us-mlops:latest $ECR_URL:latest
docker push $ECR_URL:latest

# Deploy frontend to S3
S3_BUCKET=$(terraform output -raw s3_frontend_bucket_name)
aws s3 sync ../dist/ s3://$S3_BUCKET/ --delete
```

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET (0.0.0.0/0)                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
   ┌──────────┐                         ┌──────────────┐
   │ CloudFront│                         │    ALB       │
   │  (S3 CDN) │                         │  (Port 80)   │
   └──────────┘                         └──────────────┘
        ↓                                       ↓
   ┌──────────┐                         ┌──────────────┐
   │  S3      │                         │  Target Group│
   │ Bucket   │                         │  :5000       │
   │          │                         └──────────────┘
   └──────────┘                                ↓
                                    ┌─────────────────────┐
                                    │   ECS Cluster       │
                                    │  (Fargate)          │
                                    │  ┌─────────────┐    │
                                    │  │ Task 1      │    │
                                    │  │ Flask:5000  │    │
                                    │  └─────────────┘    │
                                    │  ┌─────────────┐    │
                                    │  │ Task 2...   │    │
                                    │  │ (Auto scale)│    │
                                    │  └─────────────┘    │
                                    │                     │
                                    └─────────────────────┘
                                            ↓
                                    ┌──────────────┐
                                    │  ECR         │
                                    │  Repository  │
                                    │  (Docker)    │
                                    └──────────────┘
```

## 🔧 Configuration Variables

All variables can be customized in `terraform.tfvars`:

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | us-east-1 | AWS region |
| `environment` | dev | Environment (dev/staging/prod) |
| `container_cpu` | 256 | CPU units (256-4096) |
| `container_memory` | 512 | Memory MB (512-30720) |
| `ecs_desired_count` | 1 | Initial task count |
| `enable_load_balancer` | true | Enable ALB |
| `enable_cloudfront` | true | Enable CloudFront |
| `enable_autoscaling` | true | Enable auto-scaling |
| `autoscaling_max_capacity` | 3 | Max task count |
| `log_retention_days` | 7 | CloudWatch log retention |

## 📤 Important Outputs

After deployment, retrieve these values:

```bash
terraform output ecr_repository_url          # ECR image URL
terraform output alb_dns_name                # Backend API endpoint
terraform output s3_frontend_bucket_name     # S3 bucket name
terraform output cloudfront_domain_name      # CDN endpoint
terraform output github_actions_setup        # GitHub Actions vars
terraform output ecs_cluster_name            # ECS cluster name
```

## 🔐 Security Features

✅ **Public Access Blocked** - S3 bucket private, only CloudFront access  
✅ **VPC Isolation** - ECS tasks in private subnets  
✅ **Security Groups** - Restrictive ingress/egress rules  
✅ **IAM Roles** - Least privilege principle  
✅ **Encryption** - AES256 for S3 and CloudWatch  
✅ **Health Checks** - Container health monitoring  
✅ **Deployment Rollback** - Automatic on failure  

## 📊 Cost Estimation (Dev Environment, Monthly)

| Component | Estimated Cost |
|-----------|-----------------|
| ALB | ~$16 |
| ECS Fargate (1 task) | ~$15-30 |
| S3 | ~$1 |
| CloudFront | ~$0.50-5 |
| CloudWatch Logs | ~$0.50 |
| **Total** | **~$30-50** |

(Prices for us-east-1, may vary by region)

## 🔄 Common Operations

### Scale ECS Service

```hcl
# In terraform.tfvars
ecs_desired_count = 3
```

```bash
terraform apply
```

### Update Container Resources

```hcl
container_cpu = 512
container_memory = 1024
```

### Enable HTTPS

Add ACM certificate:
```hcl
enable_https = true
acm_certificate_arn = "arn:aws:acm:us-east-1:..."
```

### Change Auto Scaling Limits

```hcl
autoscaling_min_capacity = 2
autoscaling_max_capacity = 10
autoscaling_target_cpu = 75
```

## 📝 Deployment Checklist

- [ ] AWS account and credentials configured
- [ ] Terraform installed and validated
- [ ] `terraform.tfvars` reviewed and updated (if needed)
- [ ] `terraform plan` reviewed
- [ ] `terraform apply` completed successfully
- [ ] Outputs saved/documented
- [ ] Docker image built and pushed to ECR
- [ ] Frontend deployed to S3
- [ ] Backend health check verified (curl /model-info)
- [ ] Frontend accessible via CloudFront
- [ ] Auto-scaling tested
- [ ] CloudWatch logs monitored

## 🐛 Troubleshooting

### Common Issues

1. **"Error acquiring the state lock"**
   - State file is locked
   - Solution: `terraform force-unlock <LOCK_ID>`

2. **"Invalid provider configuration"**
   - AWS credentials not found
   - Solution: Run `aws configure`

3. **"The subnets in the load balancer..."**
   - ALB subnets not in same VPC
   - Solution: Verify VPC CIDR in terraform.tfvars

4. **"ECS task failed to start"**
   - Check CloudWatch logs: `aws logs tail /ecs/among-us-mlops-task`

### Debug Mode

```bash
export TF_LOG=DEBUG
terraform apply 2>&1 | tee debug.log
unset TF_LOG
```

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/)
- [Terraform Best Practices](https://www.terraform.io/docs/language/modules)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## ✅ What's Included

✨ **100% Infrastructure as Code** - No manual AWS console clicks  
✨ **Production-Ready** - Security, logging, monitoring built-in  
✨ **Auto-Scaling** - CPU/Memory based scaling  
✨ **Load Balancing** - High availability with ALB  
✨ **CDN Integration** - CloudFront for frontend  
✨ **Container Registry** - ECR with lifecycle policies  
✨ **Comprehensive Documentation** - Guides for every step  

## 🎯 Next Steps

1. **Read** `GETTING_STARTED.md` for step-by-step instructions
2. **Review** `terraform.tfvars` and customize if needed
3. **Run** `terraform apply` to create infrastructure
4. **Deploy** your application to S3 and ECR
5. **Monitor** with CloudWatch Logs and AWS Console

---

**Questions?** Check `QUICK_REFERENCE.md` for common commands and troubleshooting.
