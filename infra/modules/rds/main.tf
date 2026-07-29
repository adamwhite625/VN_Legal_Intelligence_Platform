resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.app_name}-db-subnet-group"
  }
}

resource "aws_rds_cluster" "mysql" {
  cluster_identifier     = "${var.app_name}-mysql"
  engine                 = "aurora-mysql"
  engine_mode            = "serverless"
  engine_version         = "5.7.mysql_aurora.2.11.4"
  database_name          = var.db_name
  master_username        = var.db_user
  master_password        = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_security_group_id]
  skip_final_snapshot    = true

  scaling_configuration {
    auto_pause               = true
    min_capacity             = 1
    max_capacity             = 2
    seconds_until_auto_pause = 300
  }

  tags = {
    Name = "${var.app_name}-mysql"
  }
}
