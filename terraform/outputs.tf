output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_repository_name" {
  description = "ECR repository name"
  value       = aws_ecr_repository.backend.name
}

output "s3_frontend_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "s3_frontend_bucket_url" {
  description = "S3 bucket website endpoint"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].domain_name : null
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].id : null
}

output "frontend_custom_domain_url" {
  description = "Custom frontend domain URL"
  value       = local.enable_custom_domain ? "https://${var.frontend_domain_name}" : null
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.main.name
}

output "ecs_task_definition_arn" {
  description = "ECS task definition ARN"
  value       = aws_ecs_task_definition.main.arn
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = var.enable_load_balancer ? aws_lb.main[0].dns_name : null
}

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = var.enable_load_balancer ? aws_lb.main[0].arn : null
}

output "iam_ecs_task_execution_role_arn" {
  description = "ECS task execution role ARN"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "iam_ecs_task_role_arn" {
  description = "ECS task role ARN"
  value       = aws_iam_role.ecs_task_role.arn
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name for ECS"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "github_actions_setup" {
  description = "GitHub Actions environment variables to set"
  value = {
    ECR_REPOSITORY             = aws_ecr_repository.backend.name
    AWS_REGION                 = var.aws_region
    ECS_CLUSTER                = aws_ecs_cluster.main.name
    ECS_SERVICE                = aws_ecs_service.main.name
    ECS_TASK_DEFINITION        = aws_ecs_task_definition.main.family
    S3_BUCKET                  = aws_s3_bucket.frontend.id
    CLOUDFRONT_DISTRIBUTION_ID = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].id : ""
  }
}
