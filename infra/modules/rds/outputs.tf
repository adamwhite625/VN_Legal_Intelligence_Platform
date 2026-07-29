output "cluster_endpoint" {
  value = aws_rds_cluster.mysql.endpoint
}

output "cluster_port" {
  value = aws_rds_cluster.mysql.port
}

output "database_name" {
  value = aws_rds_cluster.mysql.database_name
}
