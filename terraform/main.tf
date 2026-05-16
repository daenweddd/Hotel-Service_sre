terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

resource "local_file" "vm_provisioning_plan" {
  filename = "${path.module}/infrastructure-plan.txt"

  content = <<EOT
Hotel Booking SRE Infrastructure Provisioning Plan

Project Name: ${var.project_name}
Environment: ${var.environment}
Number of Virtual Machines: ${var.vm_count}

This file was generated automatically by Terraform.

VM 1: Docker Swarm Manager Node
- Purpose: Runs Docker Swarm services
- Components: API Gateway and microservices replicas
- Ports: 8080

VM 2: Kubernetes Worker Node
- Purpose: Runs Kubernetes deployments and services
- Components: Booking Service, Payment Service, Hotel Service, Room Service
- Features: self-healing, replicas, HPA

VM 3: Monitoring Node
- Purpose: Runs Prometheus and Grafana
- Ports: 9090, 3000

Database Layer:
- PostgreSQL for main relational data
- Redis for caching

Network:
- API Gateway: port 8080
- Prometheus: port 9090
- Grafana: port 3000
- PostgreSQL: port 5432
- Redis: port 6379
EOT
}