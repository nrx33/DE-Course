variable "gcp_bq_dataset_name" {
  description = "name of the bigquery dataset"
  default     = "unique_conquest_448021_n3_dtc_de_dataset"
}

variable "gcp_location" {
  description = "location of the server"
  default     = "asia-southeast1"
}

variable "gcp_bucket_name" {
  description = "name of the bucket"
  default     = "unique_conquest_448021_n3_dtc_de_bucket"
}

variable "gcp_project_id" {
  description = "project id of the gcp project"
  default     = "unique-conquest-448021-n3"
}

variable "gcp_bucket_class" {
  description = "bucket class of the gcp bucket"
  default     = "STANDARD"
}

variable "gcp_region" {
  description = "region of the project"
  default     = "asia-southeast1"
}

variable "gcp_credentials" {
  description = "location of the credentials file"
  default     = "./keys/my-creds.json"
}