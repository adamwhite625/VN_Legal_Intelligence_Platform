output "qdrant_dns_name" {
  description = "Internal DNS name for Qdrant service discovery"
  value       = "qdrant.${var.app_name}.local"
}
