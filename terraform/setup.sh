#!/bin/bash

# Terraform Infrastructure Setup Script
# Run this script to initialize and deploy infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Among Us MLOps - Terraform Setup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed${NC}"
    echo "Visit: https://www.terraform.io/downloads.html"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

terraform_version=$(terraform version -json | jq -r '.terraform_version')
echo -e "${GREEN}✓ Terraform ${terraform_version}${NC}"

aws_region=$(aws configure get region)
echo -e "${GREEN}✓ AWS CLI configured (region: ${aws_region})${NC}"

# Verify AWS credentials
echo -e "${YELLOW}[2/5] Verifying AWS credentials...${NC}"
aws_identity=$(aws sts get-caller-identity --query 'Account' --output text)
if [ -z "$aws_identity" ]; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials verified (Account: ${aws_identity})${NC}"

# Initialize Terraform
echo -e "${YELLOW}[3/5] Initializing Terraform...${NC}"
terraform init

# Validate configuration
echo -e "${YELLOW}[4/5] Validating Terraform configuration...${NC}"
terraform validate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration is valid${NC}"
else
    echo -e "${RED}Error: Configuration validation failed${NC}"
    exit 1
fi

# Format files
echo -e "${YELLOW}[5/5] Formatting Terraform files...${NC}"
terraform fmt -recursive

# Show plan
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Infrastructure Plan${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

terraform plan -out=tfplan

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Review the infrastructure plan above"
echo "2. Run: terraform apply tfplan"
echo "3. Once complete, run: terraform output -json > outputs.json"
echo "4. Build and push Docker image:"
echo "   docker build -t \$(terraform output -raw ecr_repository_url):latest .."
echo "   docker push \$(terraform output -raw ecr_repository_url):latest"
echo ""
