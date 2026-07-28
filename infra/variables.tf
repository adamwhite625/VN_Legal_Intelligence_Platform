variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "legal-chatbot"
}

variable "image_tag_backend" {
  description = "Docker image tag for backend"
  type        = string
  default     = "latest"
}

variable "image_tag_frontend" {
  description = "Docker image tag for frontend"
  type        = string
  default     = "latest"
}

variable "openai_api_key" {
  description = "OpenAI API Key stored in AWS Secrets Manager"
  type        = string
  sensitive   = true
  default     = ""
}

variable "db_password" {
  description = "Master password for RDS MySQL"
  type        = string
  sensitive   = true
  default     = "LegalBotPass2026!"
}
