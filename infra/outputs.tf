output "vpc_id" {
  value = module.network.vpc_id
}

output "backend_ecr_url" {
  value = module.ecr.backend_repository_url
}

output "frontend_ecr_url" {
  value = module.ecr.frontend_repository_url
}

output "alb_dns_name" {
  description = "Public URL for application load balancer"
  value       = module.alb.alb_dns_name
}

