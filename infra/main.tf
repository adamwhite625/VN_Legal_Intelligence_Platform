module "network" {
  source      = "./modules/network"
  app_name    = var.app_name
  environment = var.environment
}

module "ecr" {
  source   = "./modules/ecr"
  app_name = var.app_name
}

module "alb" {
  source                = "./modules/alb"
  app_name              = var.app_name
  vpc_id                = module.network.vpc_id
  public_subnet_ids     = module.network.public_subnet_ids
  alb_security_group_id = module.network.alb_security_group_id
}

module "rds" {
  source               = "./modules/rds"
  app_name             = var.app_name
  private_subnet_ids   = module.network.private_subnet_ids
  db_security_group_id = module.network.database_security_group_id
  db_name              = "law_chatbot_db"
  db_user              = "admin"
  db_password          = var.db_password
}

module "elasticache" {
  source                 = "./modules/elasticache"
  app_name               = var.app_name
  private_subnet_ids     = module.network.private_subnet_ids
  redis_security_group_id = module.network.redis_security_group_id
}

module "ecs" {
  source                       = "./modules/ecs"
  app_name                     = var.app_name
  environment                  = var.environment
  public_subnet_ids            = module.network.public_subnet_ids
  ecs_tasks_security_group_id  = module.network.ecs_tasks_security_group_id
  backend_image                = "${module.ecr.backend_repository_url}:${var.image_tag_backend}"
  frontend_image               = "${module.ecr.frontend_repository_url}:${var.image_tag_frontend}"
  backend_target_group_arn     = module.alb.backend_target_group_arn
  frontend_target_group_arn    = module.alb.frontend_target_group_arn
  openai_api_key               = var.openai_api_key
  db_host                      = module.rds.cluster_endpoint
  db_port                      = module.rds.cluster_port
  db_user                      = "admin"
  db_password                  = var.db_password
  db_name                      = "law_chatbot_db"
  qdrant_host                  = module.qdrant.qdrant_dns_name
  redis_host                   = module.elasticache.redis_endpoint
  redis_port                   = module.elasticache.redis_port
  aws_bearer_token_bedrock     = var.aws_bearer_token_bedrock
}

module "qdrant" {
  source                   = "./modules/qdrant"
  app_name                 = var.app_name
  vpc_id                   = module.network.vpc_id
  private_subnet_ids       = module.network.private_subnet_ids
  qdrant_security_group_id = module.network.qdrant_security_group_id
  cluster_id               = module.ecs.cluster_id
  execution_role_arn       = module.ecs.execution_role_arn
}
