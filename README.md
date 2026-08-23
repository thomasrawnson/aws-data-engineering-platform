# AWS Data Engineering Platform

An end-to-end data engineering project built with Python, AWS, Dagster, Terraform, GitHub Actions, and Amazon Bedrock.

The project demonstrates a realistic cloud data pipeline: ingesting source order data, storing raw data in a Bronze layer, validating and separating records into Silver and Quarantine outputs, building a Gold analytical dataset, and adding automated testing, orchestration, infrastructure as code, and CI/CD around the pipeline.

## Project Status

This project is in active development. The main data pipeline is implemented and currently includes:

* Python-based ingestion, validation, transformation, and aggregation
* AWS S3 data lake with Bronze, Silver, Quarantine, and Gold layers
* Data quality validation with quarantined invalid records
* Dagster orchestration and asset checks
* Amazon Bedrock integration for AI-assisted data quality recommendations
* Pytest test coverage for the core pipeline components
* GitHub Actions CI for automated tests
* Manual GitHub Actions workflow for running the pipeline in AWS
* Terraform-managed AWS S3, IAM, and GitHub OIDC infrastructure
* Terraform validation workflow in CI

## Architecture

```text
                    Source Orders
                         │
                         ▼
                 ┌───────────────┐
                 │    Dagster    │
                 │ Orchestration │
                 └───────┬───────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Bronze / S3    │
                │   Raw Orders    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Data Validation │
                │  + Quality      │
                │     Checks      │
                └──────┬─────┬────┘
                       │     │
                 Valid │     │ Invalid
                       ▼     ▼
              ┌──────────┐  ┌─────────────┐
              │ Silver   │  │ Quarantine  │
              │   / S3   │  │    / S3     │
              └────┬─────┘  └──────┬──────┘
                   │               │
                   ▼               ▼
              ┌──────────┐   ┌─────────────┐
              │   Gold   │   │   Bedrock   │
              │   / S3   │   │ AI Analysis │
              └──────────┘   └──────┬──────┘
                                    │
                                    ▼
                             Quality Report
```

## Technology Stack

### Data Engineering

* Python 3.12
* Pandas
* AWS S3
* Bronze, Silver, Quarantine, and Gold data layers
* Data validation and transformation

### Orchestration

* Dagster
* Dagster assets
* Dagster asset checks
* Scheduled pipeline execution

### AI-Assisted Quality Analysis

* Amazon Bedrock
* Amazon Nova Lite
* Rule-based validation with AI-assisted recommendations

### Testing and CI/CD

* Pytest
* GitHub Actions
* Automated test execution on push and pull request
* Manual workflow dispatch for running the full pipeline in AWS
* GitHub OpenID Connect authentication to AWS
* Terraform validation workflow

### Infrastructure

* Terraform
* AWS IAM
* AWS S3
* GitHub OIDC provider
* S3 versioning, encryption, ownership controls, and public access blocking

## Pipeline Overview

The pipeline processes order data through four data layers.

### Bronze

Raw source data is uploaded to Amazon S3 using date-based partitioning:

```text
bronze/orders/
└── ingestion_date=YYYY-MM-DD/
    └── orders_with_errors.csv
```

The Bronze layer preserves the source file before validation or transformation.

### Silver

Orders are validated and clean records are written to the Silver layer:

```text
silver/orders/orders_valid.csv
```

Validation currently checks for:

* Duplicate order IDs
* Missing customer IDs
* Invalid quantities
* Invalid order dates
* Missing unit prices

### Quarantine

Invalid records are written separately rather than being silently dropped:

```text
quarantine/orders/orders_invalid.csv
```

This makes data quality problems visible and traceable.

### Gold

Validated orders are aggregated into an analytical sales dataset:

```text
gold/sales/daily_product_sales.csv
```

The Gold dataset contains:

* Order date
* Product ID
* Total orders
* Total quantity
* Total sales

## Data Quality

The project uses deterministic validation rules for core data quality checks. Invalid records are separated into a Quarantine layer, while clean records continue into Silver and Gold.

Dagster asset checks are used to verify the Silver dataset. Current checks include:

* No validation errors
* Unique order IDs
* Positive quantities
* Valid unit prices

This approach keeps the pipeline predictable while making data quality issues easy to inspect.

## AI-Assisted Data Quality Analysis

Amazon Bedrock is used to generate human-readable recommendations from the validation results.

The validation layer remains rule-based and deterministic. The AI layer is used only after validation to explain issues and suggest possible follow-up actions.

```text
Invalid records
      │
      ▼
Validation rules
      │
      ▼
Quality issues
      │
      ▼
Amazon Bedrock
      │
      ▼
Recommendations
      │
      ▼
Data quality report
```

## Testing

The project uses Pytest for automated testing.

Tests currently cover:

* Bronze ingestion
* Data validation
* Silver transformations
* Gold transformations
* AI quality analysis
* AI quality reporting

The test suite is run automatically by GitHub Actions on pushes and pull requests.

## CI/CD and AWS Pipeline Execution

The project includes two main GitHub Actions workflows.

### Tests

The standard CI workflow runs the Python test suite on pushes and pull requests.

### Manual AWS Pipeline Run

A separate manual workflow runs the full Python data pipeline against AWS.

The workflow uses GitHub OpenID Connect to assume an AWS IAM role, so long-lived AWS access keys are not stored in GitHub.

The manual workflow:

* Checks out the repository
* Installs Python dependencies
* Assumes the AWS GitHub Actions IAM role using OIDC
* Verifies the AWS caller identity
* Runs the pipeline with `python -m src.pipeline.run_pipeline`
* Writes outputs to the Bronze, Silver, Quarantine, and Gold S3 layers

Verified S3 outputs include:

```text
bronze/orders/ingestion_date=YYYY-MM-DD/orders_with_errors.csv
silver/orders/orders_valid.csv
quarantine/orders/orders_invalid.csv
gold/sales/daily_product_sales.csv
```

## Infrastructure as Code

Terraform manages the AWS infrastructure used by the project.

Implemented infrastructure includes:

* Existing S3 data lake brought under Terraform management
* S3 public access blocking
* S3 server-side encryption
* S3 bucket versioning
* S3 bucket ownership controls
* GitHub OIDC provider
* GitHub Actions IAM role
* Least-privilege S3 access policy for the pipeline role
* Bedrock invoke permissions for AI-assisted quality analysis

Terraform checks are also run in GitHub Actions using:

* `terraform fmt -check`
* `terraform init -backend=false`
* `terraform validate`

```text
terraform/
├── iam.tf
├── main.tf
├── outputs.tf
└── variables.tf
```

## Project Structure

```text
aws-data-engineering-platform/
│
├── .github/
│   └── workflows/
│       ├── run-pipeline.yml
│       ├── terraform.yml
│       └── tests.yml
│
├── config/
│   └── config.yaml
│
├── data/
│   └── sample/
│
├── src/
│   ├── ai/
│   │   ├── bedrock_client.py
│   │   ├── quality_analyzer.py
│   │   ├── quality_report.py
│   │   └── ...
│   │
│   ├── dagster_project/
│   │   └── definitions.py
│   │
│   ├── gold/
│   │   └── build_gold.py
│   │
│   ├── ingestion/
│   │   └── ingest_orders.py
│   │
│   ├── pipeline/
│   │   └── run_pipeline.py
│   │
│   ├── utils/
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   └── s3.py
│   │
│   └── validation/
│       ├── order_validation.py
│       └── run_validation.py
│
├── terraform/
├── tests/
├── requirements.txt
└── README.md
```

## Engineering Practices Demonstrated

This project is intended to demonstrate practical data engineering and software engineering skills, including:

* Python application development
* ETL/ELT pipeline design
* Cloud object storage
* Data lake architecture
* Data quality engineering
* Data validation and quarantine handling
* Pipeline orchestration
* Automated testing
* CI/CD
* Secure GitHub Actions to AWS authentication using OIDC
* AI-assisted data quality reporting
* Infrastructure as code
* AWS IAM and least-privilege access
* Reproducible infrastructure management

## Recent Progress

Recent milestones completed:

* Built the Bronze, Silver, Quarantine, and Gold pipeline layers
* Added validation rules and quarantined invalid records
* Added Gold daily product sales aggregation
* Added Dagster assets and asset checks
* Added Amazon Bedrock quality recommendations
* Added Pytest coverage for the core pipeline components
* Added GitHub Actions CI for tests
* Brought the S3 data lake under Terraform management
* Added Terraform-managed GitHub OIDC and IAM role for GitHub Actions
* Added a manual GitHub Actions workflow to run the full pipeline in AWS
* Added Terraform validation checks in GitHub Actions

## Future Improvements

Planned improvements include:

* Additional data sources
* Incremental ingestion and change detection
* More comprehensive data quality checks
* Production-style configuration management
* Monitoring and alerting
* Data visualisation
* Additional AWS services
* Improved AI-generated data quality reporting

## Project Goal

The goal of this project is to demonstrate the design and implementation of a realistic cloud-based data engineering platform while applying software engineering principles such as testing, automation, orchestration, infrastructure as code, and maintainable Python development.
