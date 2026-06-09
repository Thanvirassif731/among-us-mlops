# Terraform Quick Reference

## Basic Commands

```bash
# Initialize Terraform (first time setup)
terraform init

# Validate configuration syntax
terraform validate

# Format Terraform files
terraform fmt -recursive

# Plan infrastructure changes (dry-run)
terraform plan -out=tfplan

# Apply planned changes
terraform apply tfplan

# Destroy all infrastructure
terraform destroy

# Show current outputs
terraform output
terraform output -json
```

## State Management

```bash
# List all resources
terraform state list

# Show specific resource details
terraform state show aws_ecs_service.main

# Manual state manipulation (use with caution)
terraform state mv <source> <destination>
terraform state rm <resource>
terraform state push <file>
terraform state pull > terraform.tfstate
```

## Variables

```bash
# Override variables from command line
terraform apply -var="environment=prod" -var="ecs_desired_count=3"

# Use alternate tfvars file
terraform apply -var-file="prod.tfvars"

# Export variables as environment variables
export TF_VAR_environment=prod
export TF_VAR_ecs_desired_count=3
terraform apply
```

## Useful AWS CLI Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# View ECR repository
aws ecr describe-repositories --repository-names among-us-mlops

# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# View ECS cluster status
aws ecs describe-clusters --clusters among-us-mlops-cluster

# View ECS service status
aws ecs describe-services --cluster among-us-mlops-cluster --services among-us-mlops-service

# View ECS task definition
aws ecs describe-task-definition --task-definition among-us-mlops-task

# List running tasks
aws ecs list-tasks --cluster among-us-mlops-cluster

# View task details
aws ecs describe-tasks --cluster among-us-mlops-cluster --tasks <TASK_ARN>

# View CloudWatch logs
aws logs tail /ecs/among-us-mlops-task --follow

# View ALB details
aws elbv2 describe-load-balancers --names among-us-mlops-alb

# View S3 bucket contents
aws s3 ls s3://among-us-mlops-frontend-<ACCOUNT_ID>/ --recursive
```

## Deployment Workflow

### 1. Initial Setup

```bash
cd terraform
terraform init
```

### 2. Customize Configuration

Edit `terraform.tfvars` with your settings

### 3. Validate Configuration

```bash
terraform validate
terraform fmt -recursive
```

### 4. Plan Changes

```bash
terraform plan -out=tfplan
# Review the plan output carefully
```

### 5. Apply Changes

```bash
terraform apply tfplan
```

### 6. Get Outputs

```bash
terraform output -json > infrastructure-outputs.json
```

### 7. Build and Push Docker Image

```bash
ECR_URL=$(terraform output -raw ecr_repository_url)
docker build -t $ECR_URL:latest ..
docker push $ECR_URL:latest
```

### 8. Update ECS Service (optional)

ECS service will automatically pull the latest image from ECR.

```bash
# Force new deployment
aws ecs update-service \
  --cluster among-us-mlops-cluster \
  --service among-us-mlops-service \
  --force-new-deployment
```

## Modifying Infrastructure

### Scale Up ECS Service

```hcl
# In terraform.tfvars
ecs_desired_count = 2
```

```bash
terraform plan
terraform apply
```

### Update Container Resources

```hcl
# In terraform.tfvars
container_cpu    = 512  # was 256
container_memory = 1024 # was 512
```

```bash
terraform plan
terraform apply
```

This may cause a brief service interruption as new tasks are deployed.

### Enable/Disable Auto Scaling

```hcl
enable_autoscaling = true
autoscaling_max_capacity = 5
```

### Update Environment Variables

```hcl
# Edit ecs.tf - container_definitions - environment section
```

Then:

```bash
terraform plan
terraform apply
```

## Debugging

### Enable Debug Logging

```bash
export TF_LOG=DEBUG
terraform plan 2>&1 | tee debug.log
unset TF_LOG
```

### Validate AWS Credentials

```bash
aws sts get-caller-identity
aws ec2 describe-regions
```

### Check Terraform Backend

```bash
terraform state list
terraform state show aws_ecs_cluster.main
```

### View Resource Outputs

```bash
# Display specific output
terraform output ecr_repository_url

# Display all outputs as JSON
terraform output -json
```

## Workspace Management

Use workspaces for multiple environments:

```bash
# List workspaces
terraform workspace list

# Create workspace
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# Delete workspace
terraform workspace delete staging

# Show current workspace
terraform workspace show
```

Use with different tfvars:
```bash
terraform apply -var-file="prod.tfvars"
```

## Cost Estimation

```bash
# Install Infracost (optional)
curl https://ew.infracost.io/scripts/install.sh | sh

# Estimate costs
infracost breakdown --path .
```

## Backup and Recovery

### Backup State

```bash
cp terraform.tfstate terraform.tfstate.backup
```

### Remote State Backend (recommended for production)

Create `backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "mlops/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

Initialize:

```bash
terraform init
```

## Security Best Practices

1. **Store tfvars securely** - Never commit sensitive values
2. **Use remote state** - Store state in S3 with encryption
3. **Enable state locking** - Use DynamoDB for state locks
4. **Rotate credentials** - Regularly update AWS access keys
5. **Use IAM roles** - Prefer roles over long-term credentials
6. **Audit logs** - Enable CloudTrail for infrastructure changes
7. **Secret management** - Use AWS Secrets Manager or Parameter Store

## Common Issues

| Issue | Solution |
|-------|----------|
| "Error: No valid credential sources found" | Run `aws configure` |
| "Error acquiring the state lock" | Delete stale lock or fix backend access |
| "Error: Invalid provider configuration" | Check AWS region and credentials |
| "Error: resource already exists" | Check state file or AWS console |
| "Error: The subnets in the load balancer..." | Ensure subnets are in same VPC |

## Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform.io/language/modules)
- [Infrastructure as Code Best Practices](https://aws.amazon.com/blogs/devops/infrastructure-as-code/)
