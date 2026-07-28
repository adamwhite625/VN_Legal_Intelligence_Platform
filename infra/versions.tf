terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket = "legal-chatbot-tfstate-381149551435"
    key    = "legal-chatbot/terraform.tfstate"
    region = "ap-southeast-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "VN-Legal-Chatbot"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
