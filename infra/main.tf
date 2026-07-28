module "network" {
  source      = "./modules/network"
  app_name    = var.app_name
  environment = var.environment
}

module "ecr" {
  source   = "./modules/ecr"
  app_name = var.app_name
}
