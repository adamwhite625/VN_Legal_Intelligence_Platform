output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

output "private_subnet_ids" {
  value = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

output "alb_security_group_id" {
  value = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  value = aws_security_group.ecs_tasks.id
}

output "database_security_group_id" {
  value = aws_security_group.database.id
}

output "redis_security_group_id" {
  value = aws_security_group.redis.id
}

output "qdrant_security_group_id" {
  value = aws_security_group.qdrant.id
}
