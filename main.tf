terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = "us-east-1" # Change to your preferred AWS region
}

# 1. Create S3 Bucket
resource "aws_s3_bucket" "resume_bucket" {
  
  bucket = "resume-processing-bucket"
  acl    = "private"

  tags= {
    Name = "Resume Processing Bucket"
    Environment = "Dev"
  }
  versioning {
    enabled = true
  }
}

# 2. Create IAM Role and Policies for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_s3_access_policy" {
  name        = "lambda_s3_access_policy"
  description = "Policy for Lambda to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.resume_bucket.arn,
          "${aws_s3_bucket.resume_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_lambda_s3_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_s3_access_policy.arn
}

# 3. Create Lambda Layer
resource "aws_lambda_layer_version" "shared_layer" {
  filename         = "./layer.zip" # Path to your pre-created zip file for the layer
  layer_name       = "shared_dependencies_layer"
  compatible_runtimes = ["python3.9"]
}

# 4. Create Lambda Functions
resource "aws_lambda_function" "process_resume" {
  function_name    = "processResume"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "process_resume.lambda_handler" # Update with your actual handler name
  filename         = "./processResume.zip" # Path to the zip file of your code

  layers = [
    aws_lambda_layer_version.shared_layer.arn
  ]

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.resume_bucket.bucket
    }
  }
}

resource "aws_lambda_function" "search_resume" {
  function_name    = "searchResume"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "search_resume.lambda_handler" # Update with your actual handler name
  filename         = "./searchResume.zip" # Path to the zip file of your code

  layers = [
    aws_lambda_layer_version.shared_layer.arn
  ]

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.resume_bucket.bucket
    }
  }
}

# 5. Add S3 Event Notification to Trigger processResume Lambda
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.resume_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_resume.arn
    events              = ["s3:ObjectCreated:Put"]
  }
}

# Grant S3 permission to invoke the Lambda function
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_resume.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.resume_bucket.arn
}
