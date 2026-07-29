variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "ecs_tasks_security_group_id" {
  type = string
}

variable "backend_image" {
  type = string
}

variable "frontend_image" {
  type = string
}

variable "backend_target_group_arn" {
  type = string
}

variable "frontend_target_group_arn" {
  type = string
}

variable "openai_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "db_host" {
  description = "RDS MySQL endpoint"
  type        = string
}

variable "db_port" {
  description = "RDS MySQL port"
  type        = number
  default     = 3306
}

variable "db_user" {
  type    = string
  default = "root"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_name" {
  type    = string
  default = "law_chatbot_db"
}

variable "qdrant_host" {
  description = "Qdrant service discovery DNS name"
  type        = string
}

variable "redis_host" {
  description = "ElastiCache Redis endpoint"
  type        = string
}

variable "redis_port" {
  description = "ElastiCache Redis port"
  type        = number
  default     = 6379
}

variable "secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
  default     = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
}

variable "bedrock_model_id" {
  type    = string
  default = "openai.gpt-oss-120b-1:0"
}

variable "bedrock_region" {
  type    = string
  default = "ap-northeast-1"
}

variable "aws_bearer_token_bedrock" {
  type      = string
  sensitive = true
  default   = ""
}
