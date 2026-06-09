# 🎯 Terraform Deployment Checklist

## ✅ What You Have

- [x] Complete Terraform Infrastructure Code (1000+ lines)
- [x] VPC with public/private subnets
- [x] S3 bucket with CloudFront CDN
- [x] ECR repository for Docker images
- [x] ECS Fargate cluster with auto-scaling
- [x] Application Load Balancer
- [x] CloudWatch Logs & Monitoring
- [x] IAM roles with least privilege
- [x] Security groups
- [x] Comprehensive documentation

## 📋 Pre-Deployment Checklist

### Prerequisites
- [ ] AWS Account created
- [ ] AWS CLI installed and configured
  ```bash
  aws configure
  aws sts get-caller-identity
  ```
- [ ] Terraform installed (version >= 1.0)
  ```bash
  terraform version
  ```
- [ ] Docker installed (for building images)
  ```bash
  docker version
  ```

### Configuration Review
- [ ] Review `terraform/terraform.tfvars`
- [ ] Verify AWS region is correct
- [ ] Check environment setting (dev/staging/prod)
- [ ] Validate container CPU/Memory settings

## 🚀 Deployment Steps

### 1. Initialize Terraform
- [ ] Navigate to terraform directory: `cd terraform`
- [ ] Run initialization: `terraform init`
- [ ] Validate configuration: `terraform validate`
- [ ] Format files: `terraform fmt -recursive`

### 2. Plan Infrastructure
- [ ] Review plan: `terraform plan -out=tfplan`
- [ ] Check resource count (should be 40+)
- [ ] Verify no errors in output
- [ ] Estimate cost is acceptable

### 3. Create Infrastructure
- [ ] Run apply: `terraform apply tfplan`
- [ ] Wait 5-10 minutes for completion
- [ ] Verify "Apply complete" message
- [ ] Check for any warnings

### 4. Capture Outputs
- [ ] Save outputs: `terraform output`
- [ ] Export to JSON: `terraform output -json > infrastructure.json`
- [ ] Document important values:
  - [ ] ECR Repository URL
  - [ ] ALB DNS Name
  - [ ] S3 Bucket Name
  - [ ] CloudFront Domain (if enabled)

## 🐳 Backend Deployment

### Build Docker Image
- [ ] Navigate to project root: `cd ..`
- [ ] Build image: `docker build -t among-us-mlops:latest .`
- [ ] Verify build successful

### Push to ECR
- [ ] Go back to terraform: `cd terraform`
- [ ] Get ECR URL: `ECR_URL=$(terraform output -raw ecr_repository_url)`
- [ ] Login to ECR: `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL`
- [ ] Tag image: `docker tag among-us-mlops:latest $ECR_URL:latest`
- [ ] Push image: `docker push $ECR_URL:latest`
- [ ] Verify in AWS Console or: `aws ecr describe-images --repository-name among-us-mlops`

### Verify ECS Deployment
- [ ] Wait 2-3 minutes for ECS task to start
- [ ] Check service status: `aws ecs describe-services --cluster among-us-mlops-cluster --services among-us-mlops-service`
- [ ] Verify running count shows 1 or more
- [ ] Check CloudWatch logs: `aws logs tail /ecs/among-us-mlops-task --follow`

## 🌐 Frontend Deployment

### Build Frontend Assets
- [ ] Go to project root: `cd ..`
- [ ] Create dist directory: `mkdir -p dist`
- [ ] Copy index.html: `cp index.html dist/`
- [ ] Copy assets: `cp -r assets dist/` (if exists)

### Upload to S3
- [ ] Go back to terraform: `cd terraform`
- [ ] Get S3 bucket: `S3_BUCKET=$(terraform output -raw s3_frontend_bucket_name)`
- [ ] Upload files: `aws s3 sync ../dist/ s3://$S3_BUCKET/ --delete`
- [ ] Verify upload: `aws s3 ls s3://$S3_BUCKET/ --recursive`

### Invalidate CloudFront Cache (if enabled)
- [ ] Get distribution ID: `DIST_ID=$(terraform output -raw cloudfront_distribution_id)`
- [ ] Create invalidation: `aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"`
- [ ] Wait 1-2 minutes for invalidation to complete

## ✅ Testing & Verification

### Backend Testing
- [ ] Get ALB DNS: `ALB_DNS=$(terraform output -raw alb_dns_name)`
- [ ] Test health endpoint: `curl http://$ALB_DNS/model-info`
- [ ] Test prediction endpoint:
  ```bash
  curl -X POST http://$ALB_DNS/predict \
    -H "Content-Type: application/json" \
    -d '{
      "Team": "Crewmate",
      "Task Completed": 5,
      "Imposter Kills": 0,
      "Game Length Sec": 300
    }'
  ```
- [ ] Verify successful response with predictions

### Frontend Testing
- [ ] Get S3 URL: `S3_URL=$(terraform output -raw s3_frontend_bucket_url)`
- [ ] Get CloudFront URL: `CF_URL=$(terraform output -raw cloudfront_domain_name)`
- [ ] Test S3: `curl $S3_URL/index.html | head -20`
- [ ] Test CloudFront: `curl $CF_URL/index.html | head -20`
- [ ] Open in browser: `open http://$CF_URL` (or your CDN domain)

### Infrastructure Verification
- [ ] Check ECS cluster in AWS Console
- [ ] Verify 1+ tasks running
- [ ] Check ALB target groups (should be healthy)
- [ ] View CloudWatch logs
- [ ] Verify auto-scaling metrics available

## 🔒 Security Verification

- [ ] S3 public access is blocked
- [ ] Only CloudFront can access S3
- [ ] ECS tasks are in private subnets
- [ ] Security groups restrict traffic appropriately
- [ ] IAM roles have minimal permissions
- [ ] ECR image scanning is enabled
- [ ] CloudWatch logs are retained

## 📊 Monitoring Setup

- [ ] Access CloudWatch Dashboard: `aws cloudwatch list-dashboards`
- [ ] Check ECS metrics available
- [ ] Verify auto-scaling policies active
- [ ] Monitor logs: `aws logs tail /ecs/among-us-mlops-task --follow`

## 🔄 Post-Deployment Tasks

- [ ] **GitHub Actions**: Update secrets with terraform outputs
  - [ ] `AWS_ROLE_ARN` (OIDC role)
  - [ ] `CLOUDFRONT_DISTRIBUTION_ID`
  
- [ ] **Documentation**: Update deployment guide with:
  - [ ] Backend API endpoint (ALB DNS)
  - [ ] Frontend endpoint (CloudFront domain)
  - [ ] ECR repository URL

- [ ] **Monitoring**: Set up alerts for:
  - [ ] ECS task failures
  - [ ] ALB unhealthy targets
  - [ ] High CPU/Memory usage

- [ ] **Backup**: Create backups of:
  - [ ] terraform.tfstate
  - [ ] infrastructure.json (outputs)
  - [ ] terraform.tfvars (with secrets removed)

## 🧪 Testing Auto-Scaling (Optional)

- [ ] Generate load test:
  ```bash
  ALB_DNS=$(terraform output -raw alb_dns_name)
  for i in {1..100}; do
    curl -X POST http://$ALB_DNS/predict \
      -H "Content-Type: application/json" \
      -d '{"Team":"Crewmate","Task Completed":5,"Imposter Kills":0,"Game Length Sec":300}' &
  done
  ```

- [ ] Monitor scaling:
  ```bash
  while true; do
    aws ecs describe-services \
      --cluster among-us-mlops-cluster \
      --services among-us-mlops-service \
      --query 'services[0].{Running:runningCount,Desired:desiredCount}'
    sleep 10
  done
  ```

- [ ] Verify tasks scale up/down based on CPU/Memory

## 🐛 Troubleshooting Steps

If something goes wrong:

1. **Check Terraform State**
   ```bash
   terraform state list
   terraform state show aws_ecs_service.main
   ```

2. **View CloudWatch Logs**
   ```bash
   aws logs tail /ecs/among-us-mlops-task --follow
   ```

3. **Check ECS Service**
   ```bash
   aws ecs describe-services --cluster among-us-mlops-cluster --services among-us-mlops-service
   ```

4. **Debug Mode**
   ```bash
   export TF_LOG=DEBUG
   terraform plan 2>&1 | tee debug.log
   ```

## 📝 Documentation

- [ ] Read and save: `INFRASTRUCTURE_OVERVIEW.md`
- [ ] Read and save: `GETTING_STARTED.md`
- [ ] Keep reference: `QUICK_REFERENCE.md`
- [ ] Review: `README.md`

## 🎓 Learning Resources

- [ ] Terraform AWS Provider Docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- [ ] AWS ECS Best Practices: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/
- [ ] Terraform Best Practices: https://www.terraform.io/docs/language

## ✅ Final Sign-Off

- [ ] All resources deployed successfully
- [ ] Backend API responding to requests
- [ ] Frontend accessible via CloudFront
- [ ] Auto-scaling policies active
- [ ] Monitoring and logging operational
- [ ] Documentation reviewed
- [ ] Team informed of deployment
- [ ] Backup of infrastructure taken

## 📞 Quick Help

If stuck, check these in order:

1. `terraform/GETTING_STARTED.md` - Step-by-step guide
2. `terraform/QUICK_REFERENCE.md` - Common commands
3. `terraform/README.md` - Full reference
4. `terraform output` - View infrastructure values
5. AWS Console - Visual verification

---

**Total Deployment Time**: ~20-30 minutes (including testing)

**Success Criteria**:
✅ Terraform apply completes  
✅ Docker image pushed to ECR  
✅ Frontend files in S3  
✅ Backend API responding  
✅ Frontend accessible  

You're ready to deploy! 🚀
