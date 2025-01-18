terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.16.0"
    }
  }
}

provider "google" {
  project     = var.gcp_project_id
  region      = var.gcp_region
  credentials = file(var.gcp_credentials)
}

resource "google_storage_bucket" "dtc-de-bucket" {
  name          = var.gcp_bucket_name
  location      = var.gcp_location
  storage_class = var.gcp_bucket_class
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "dtc-de-dataset" {
  dataset_id                 = var.gcp_bq_dataset_name
  location                   = var.gcp_location
  delete_contents_on_destroy = true
}