variable "project_name" {
  description = "Project name"
  type        = string
  default     = "hotel-booking-sre-project"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "development"
}

variable "vm_count" {
  description = "Number of virtual machines"
  type        = number
  default     = 3
}