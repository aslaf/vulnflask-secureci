terraform {
  required_version = ">= 1.5.6"
}

provider "aws" {
  region = "us-east-1"
}

# Public S3 bucket
resource "aws_s3_bucket" "demo_bucket" {
  bucket = "vulnflask-demo-bucket"
  acl    = "public-read"   # This shall trigger Checkov finding

  tags = {
    Name        = "VulnFlask Demo Bucket"
    Environment = "dev"
  }
}

# Simple VPC
resource "aws_vpc" "demo_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "VulnFlask VPC"
  }
}
