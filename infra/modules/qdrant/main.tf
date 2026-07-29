# EFS for persistent Qdrant vector storage
resource "aws_efs_file_system" "qdrant" {
  creation_token = "${var.app_name}-qdrant-efs"
  encrypted      = true

  tags = {
    Name = "${var.app_name}-qdrant-efs"
  }
}

resource "aws_efs_mount_target" "qdrant_a" {
  file_system_id  = aws_efs_file_system.qdrant.id
  subnet_id       = var.private_subnet_ids[0]
  security_groups = [var.qdrant_security_group_id]
}

resource "aws_efs_mount_target" "qdrant_b" {
  file_system_id  = aws_efs_file_system.qdrant.id
  subnet_id       = var.private_subnet_ids[1]
  security_groups = [var.qdrant_security_group_id]
}

# EFS access point for Qdrant data directory
resource "aws_efs_access_point" "qdrant" {
  file_system_id = aws_efs_file_system.qdrant.id

  posix_user {
    gid = 1000
    uid = 1000
  }

  root_directory {
    path = "/qdrant/storage"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }
}

resource "aws_cloudwatch_log_group" "qdrant" {
  name              = "/ecs/${var.app_name}-qdrant"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "qdrant" {
  family                   = "${var.app_name}-qdrant"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.execution_role_arn

  volume {
    name = "qdrant-storage"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.qdrant.id
      transit_encryption = "ENABLED"
      authorization_configuration {
        access_point_id = aws_efs_access_point.qdrant.id
        iam             = "DISABLED"
      }
    }
  }

  container_definitions = jsonencode([
    {
      name      = "qdrant"
      image     = "qdrant/qdrant:latest"
      essential = true
      portMappings = [
        { containerPort = 6333, hostPort = 6333 },
        { containerPort = 6334, hostPort = 6334 }
      ]
      mountPoints = [
        {
          sourceVolume  = "qdrant-storage"
          containerPath = "/qdrant/storage"
          readOnly      = false
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.qdrant.name
          "awslogs-region"        = "ap-southeast-1"
          "awslogs-stream-prefix" = "qdrant"
        }
      }
    }
  ])
}

# Qdrant runs as an internal ECS service (no ALB, accessed by private IP via service discovery)
resource "aws_service_discovery_private_dns_namespace" "main" {
  name = "${var.app_name}.local"
  vpc  = var.vpc_id
}

resource "aws_service_discovery_service" "qdrant" {
  name = "qdrant"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_ecs_service" "qdrant" {
  name            = "${var.app_name}-qdrant"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.qdrant.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  platform_version = "1.4.0"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.qdrant_security_group_id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.qdrant.arn
  }

  depends_on = [
    aws_efs_mount_target.qdrant_a,
    aws_efs_mount_target.qdrant_b
  ]
}
