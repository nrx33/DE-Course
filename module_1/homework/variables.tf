variable "credentials" {
  description = "My Credentials"
  default     = "/workspaces/DE-Course/module_1/terraform/keys/my-creds.json"
  #ex: if you have a directory where this file is called keys with your service account json file
  #saved there as my-creds.json you could use default = "./keys/my-creds.json"
}


variable "project" {
  description = "Project"
  default     = "unique-conquest-448021-n3"
}

variable "region" {
  description = "Region"
  #Update the below to your desired region
  default = "asia"
}

variable "location" {
  description = "Project Location"
  #Update the below to your desired location
  default = "asia-southeast1"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  #Update the below to what you want your dataset to be called
  default = "unique_conquest_448021_n3_dtc_de_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  #Update the below to a unique bucket name
  default = "unique_conquest_448021_n3_dtc_de_bucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}