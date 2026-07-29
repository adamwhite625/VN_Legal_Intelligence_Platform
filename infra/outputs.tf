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

output "rds_endpoint" {
  description = "RDS MySQL cluster endpoint"
  value       = module.rds.cluster_endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.redis_endpoint
}

output "qdrant_dns" {
  description = "Qdrant internal DNS name"
  value       = module.qdrant.qdrant_dns_name
}
