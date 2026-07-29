resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.app_name}-redis-subnet"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.app_name}-redis-subnet"
  }
}

# Serverless ElastiCache for minimal cost
resource "aws_elasticache_serverless_cache" "redis" {
  engine = "redis"
  name   = "${var.app_name}-redis"

  cache_usage_limits {
    data_storage {
      maximum = 1
      unit    = "GB"
    }

    ecpu_per_second {
      maximum = 1000
    }
  }

  subnet_ids         = var.private_subnet_ids
  security_group_ids = [var.redis_security_group_id]

  tags = {
    Name = "${var.app_name}-redis"
  }
}
