variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "among-us-mlops"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# S3 Frontend Configuration
variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend"
  type        = string
  default     = "among-us-mlops-frontend"
}

variable "frontend_domain_name" {
  description = "Custom domain name for the frontend"
  type        = string
  default     = "among-us.thanvirassif.com"
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for the custom frontend domain"
  type        = string
  default     = null
}

variable "route53_zone_name" {
  description = "Route53 hosted zone name (e.g. thanvirassif.com) to look up the hosted zone ID if `route53_zone_id` is not provided"
  type        = string
  default     = null
}

variable "enable_cloudfront" {
  description = "Enable CloudFront distribution for S3"
  type        = bool
  default     = true
}

variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}

# ECR Configuration
variable "ecr_repository_name" {
  description = "ECR repository name"
  type        = string
  default     = "among-us-mlops"
}

variable "ecr_scan_on_push" {
  description = "Enable ECR image scanning on push"
  type        = bool
  default     = true
}

# ECS Configuration
variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
  default     = "among-us-mlops-cluster"
}

variable "ecs_service_name" {
  description = "ECS service name"
  type        = string
  default     = "among-us-mlops-service"
}

variable "ecs_task_family" {
  description = "ECS task family name"
  type        = string
  default     = "among-us-mlops-task"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 5000
}

variable "container_cpu" {
  description = "ECS task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "ECS task memory in MB"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of ECS task replicas"
  type        = number
  default     = 1
}

# Load Balancer Configuration
variable "enable_load_balancer" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = true
}

variable "alb_port" {
  description = "Load balancer port"
  type        = number
  default     = 80
}

# VPC Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

# Auto Scaling Configuration
variable "enable_autoscaling" {
  description = "Enable auto scaling for ECS service"
  type        = bool
  default     = true
}

variable "autoscaling_min_capacity" {
  description = "Minimum task count for autoscaling"
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum task count for autoscaling"
  type        = number
  default     = 3
}

variable "autoscaling_target_cpu" {
  description = "Target CPU utilization for autoscaling"
  type        = number
  default     = 70
}

# Logging Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

# Tags
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Team    = "MLOps"
    Purpose = "ML Model Serving"
  }
}
