output "bucket_id" {
  value = aws_s3_bucket.main.id
}

output "bucket_arn" {
  value = aws_s3_bucket.main.arn
}

output "policy_arn" {
  value = aws_iam_policy.s3_access.arn
}
