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

module "ecs" {
  source                       = "./modules/ecs"
  app_name                     = var.app_name
  environment                  = var.environment
  public_subnet_ids            = module.network.public_subnet_ids
  ecs_tasks_security_group_id = module.network.ecs_tasks_security_group_id
  backend_image                = "${module.ecr.backend_repository_url}:${var.image_tag_backend}"
  frontend_image               = "${module.ecr.frontend_repository_url}:${var.image_tag_frontend}"
  backend_target_group_arn     = module.alb.backend_target_group_arn
  frontend_target_group_arn    = module.alb.frontend_target_group_arn
  openai_api_key               = var.openai_api_key
}

