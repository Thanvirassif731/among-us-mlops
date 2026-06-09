# AWS Deployment Setup Guide

This guide explains how to set up and deploy the Among Us MLOps project to AWS using GitHub Actions.

## Overview

The deployment pipeline consists of:
- **Frontend**: Deployed to AWS S3 with optional CloudFront CDN
- **Backend**: Containerized with Docker and deployed to AWS ECS (Elastic Container Service)

## Prerequisites

Before you start, ensure you have:
1. AWS Account with appropriate permissions
2. GitHub repository connected to this project
3. Docker installed locally (for testing)
4. AWS CLI configured locally

## AWS Setup Steps

### 1. Create ECR Repository

```bash
aws ecr create-repository --repository-name among-us-mlops --region us-east-1
```

### 2. Create S3 Bucket for Frontend

```bash
aws s3 mb s3://among-us-mlops-frontend --region us-east-1

# Enable static website hosting
aws s3api put-bucket-website --bucket among-us-mlops-frontend --website-configuration '{
  "IndexDocument": {"Suffix": "index.html"},
  "ErrorDocument": {"Key": "index.html"}
}'

# Block public access (if using CloudFront)
aws s3api put-public-access-block --bucket among-us-mlops-frontend --public-access-block-configuration '{"BlockPublicAcls":true,"IgnorePublicAcls":true,"BlockPublicPolicy":true,"RestrictPublicBuckets":true}'
```

### 3. Set Up ECS Cluster

```bash
aws ecs create-cluster --cluster-name among-us-mlops-cluster --region us-east-1
```

### 4. Create IAM Roles

Create execution role:
```bash
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}'

aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

Create task role:
```bash
aws iam create-role --role-name ecsTaskRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}'
```

### 5. Create CloudFront Distribution (Optional)

```bash
aws cloudfront create-distribution --distribution-config-with-tags file://cloudfront-config.json
```

## GitHub Actions Configuration

### 1. Set GitHub Secrets

In your GitHub repository settings, add these secrets:

- `AWS_ROLE_ARN`: The ARN of your OIDC role for GitHub Actions
  - Format: `arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole`

- `CLOUDFRONT_DISTRIBUTION_ID` (Optional): CloudFront distribution ID for cache invalidation
  - Example: `E1234ABCD`

### 2. Create OIDC Provider for GitHub Actions

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

Create a trust policy document (`trust-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:YOUR_USERNAME/REPO_NAME:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

Create the role:
```bash
aws iam create-role --role-name GitHubActionsRole --assume-role-policy-document file://trust-policy.json
```

Attach policies:
```bash
aws iam attach-role-policy --role-name GitHubActionsRole --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPushOnly
aws iam attach-role-policy --role-name GitHubActionsRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name GitHubActionsRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceRoleForECS
aws iam attach-role-policy --role-name GitHubActionsRole --policy-arn arn:aws:iam::aws:policy/CloudFrontFullAccess
```

## Local Testing

### Build Docker Image Locally

```bash
docker build -t among-us-mlops:latest .
```

### Run Container Locally

```bash
docker run -p 5000:5000 among-us-mlops:latest
```

### Test Backend Endpoints

```bash
# Get model info
curl http://localhost:5000/model-info

# Make a prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Team": "Crewmate",
    "Task Completed": 5,
    "Imposter Kills": 0,
    "Game Length Sec": 300
  }'
```

## Deployment Process

### Manual Deployment Steps

1. **Push to main branch**:
   ```bash
   git push origin main
   ```

2. **GitHub Actions automatically**:
   - Builds Docker image
   - Pushes to ECR
   - Updates ECS service
   - Deploys frontend to S3
   - Invalidates CloudFront cache (if configured)

### Monitoring Deployments

Check GitHub Actions logs:
- Go to your repository → Actions tab
- Click on the deployment workflow
- View logs for each step

Monitor ECS deployment:
```bash
aws ecs describe-services --cluster among-us-mlops-cluster --services among-us-mlops-service --region us-east-1
```

Check S3 deployment:
```bash
aws s3 ls s3://among-us-mlops-frontend/ --recursive --region us-east-1
```

## Environment Variables

Update in `.github/workflows/deploy.yml`:
- `AWS_REGION`: Your AWS region (default: us-east-1)
- `ECR_REPOSITORY`: ECR repository name
- `ECS_SERVICE`: ECS service name
- `ECS_CLUSTER`: ECS cluster name
- `S3_BUCKET`: S3 bucket name for frontend

Update in `among-us-mlops-task.json`:
- `ACCOUNT_ID`: Your AWS account ID
- `AWS_REGION`: Your AWS region
- Container CPU/Memory: Adjust based on your needs

## Troubleshooting

### Docker Build Fails
- Ensure all dependencies in `requirements.txt` are available
- Check that model files exist in `models/` directory
- Verify Dockerfile syntax

### ECR Push Fails
- Check AWS credentials in GitHub Actions
- Verify ECR repository exists
- Ensure IAM role has `ecr:*` permissions

### ECS Deployment Fails
- Check task definition syntax in `among-us-mlops-task.json`
- Verify ECS cluster and service exist
- Check CloudWatch logs for container errors

### S3 Upload Fails
- Verify S3 bucket exists
- Check IAM permissions for S3
- Ensure bucket name is globally unique

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [GitHub Actions AWS Documentation](https://github.com/aws-actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [AWS S3 Static Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
