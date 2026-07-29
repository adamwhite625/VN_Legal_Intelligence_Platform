variable "app_name" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "db_security_group_id" {
  type = string
}

variable "db_name" {
  type    = string
  default = "law_chatbot_db"
}

variable "db_user" {
  type    = string
  default = "root"
}

variable "db_password" {
  type      = string
  sensitive = true
}
