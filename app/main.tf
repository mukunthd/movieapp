variable "AutoScalingGroup" {
  description = "AutoScalingGroup"
  type        = string
}

variable "EksCluster" {
  description = "EksCluster"
  type        = string
}

resource "aws_autoscaling_lifecycle_hook" "lifecycle_hook" {
  name                   = "lifecycle_hook"
  autoscaling_group_name = var.AutoScalingGroup
  lifecycle_transition   = "autoscaling:EC2_INSTANCE_TERMINATING"
  heartbeat_timeout      = 450
}

resource "aws_iam_role" "drainer_role" {
  name               = "drainer_role"
  path               = "/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF

}

resource "aws_iam_role_policy" "drainer_policies" {
  name = "drainer_policies"
  role = aws_iam_role.drainer_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "autoscaling:CompleteLifecycleAction",
        "ec2:DescribeInstances",
        "eks:DescribeCluster",
        "sts:GetCallerIdentity"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_lambda_function" "drainer_function" {
  filename      = "your_lambda_function_file.py.zip"
  function_name = "drainer_function"
  role          = aws_iam_role.drainer_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.7"

  environment {
    variables = {
      CLUSTER_NAME = var.EksCluster
    }
  }
}

resource "aws_cloudwatch_event_rule" "termination_event" {
  name        = "termination_event"
  description = "Triggered when EC2 instance terminates in AutoScaling Group"

  event_pattern = <<EOF
{
  "source": [
    "aws.autoscaling"
  ],
  "detail-type": [
    "EC2 Instance-terminate Lifecycle Action"
  ],
  "detail": {
    "AutoScalingGroupName": [
      "${var.AutoScalingGroup}"
    ]
  }
}
EOF
}

resource "aws_cloudwatch_event_target" "event_target" {
  rule      = aws_cloudwatch_event_rule.termination_event.id
  target_id = "drainer_function"
  arn       = aws_lambda_function.drainer_function.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.drainer_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.termination_event.arn
}

output "drainer_role_arn" {
  description = "The ARN of the drainer role"
  value       = aws_iam_role.drainer_role.arn
}
