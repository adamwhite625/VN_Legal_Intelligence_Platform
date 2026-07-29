variable "app_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "qdrant_security_group_id" {
  type = string
}

variable "cluster_id" {
  type = string
}

variable "execution_role_arn" {
  type = string
}
