provider "kubernetes" {
  config_path = "/tmp/kubeconfig"
}

resource "kubernetes_cluster_role" "lambda_cluster_access" {
  metadata {
    name = "lambda-cluster-access_new"
  }
  rule {
    api_groups = [""]
    resources  = ["pods", "pods/eviction", "nodes"]
    verbs      = ["create", "list", "patch"]
  }
}

resource "kubernetes_cluster_role_binding" "lambda_user_cluster_role_binding" {
  metadata {
    name = "lambda-user-cluster-role-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "lambda-cluster-access_new"
  }
  subject {
    kind      = "User"
    name      = "lambda"
    api_group = "rbac.authorization.k8s.io"
  }
  depends_on = [
    kubernetes_cluster_role.lambda_cluster_access
  ]
}


data "aws_iam_role" "existing_role" {
  name = "drainer_role"
}

resource "kubernetes_config_map" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    mapRoles = <<YAML
- rolearn: ${data.aws_iam_role.existing_role.arn}
  username: lambda
  groups:
  - system:masters
YAML
  }

  depends_on = [
    aws_iam_role.drainer_role
  ]
}
