output "cluster_endpoint" {
  value = aws_db_instance.mysql.address
}

output "cluster_port" {
  value = aws_db_instance.mysql.port
}

output "database_name" {
  value = aws_db_instance.mysql.db_name
}
