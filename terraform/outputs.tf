output "project_name" {
  value = var.project_name
}

output "environment" {
  value = var.environment
}

output "infrastructure_plan_file" {
  value = local_file.vm_provisioning_plan.filename
}