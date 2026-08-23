# AWS Data Engineering Platform

An end-to-end data engineering platform demonstrating modern data engineering practices using Python, AWS, data quality validation, orchestration, AI/LLMs, testing, CI/CD, and infrastructure as code.

## Project Status

🚧 In development

The core data pipeline, orchestration, automated data quality checks, AI analysis, CI/CD pipeline, GitHub Actions to AWS authentication, and Terraform-managed AWS infrastructure are currently implemented.

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

## Technologies

### Data Engineering

* Python 3.12
* Pandas
* AWS S3
* Data validation and transformation
* Bronze / Silver / Gold architecture

### Orchestration

* Dagster
* Dagster assets
* Dagster asset checks
* Scheduled pipeline execution

### AI

* Amazon Bedrock
* Amazon Nova Lite
* AI-assisted data quality analysis
* Automated quality recommendations

### Testing & CI/CD

* Pytest
* GitHub Actions
* Automated test execution on push and pull request
* Manual workflow dispatch for running the full pipeline in AWS
* GitHub OpenID Connect authentication to AWS

### Infrastructure

* Terraform
* AWS IAM
* AWS S3
* S3 versioning, encryption, ownership controls, and public access blocking

## Pipeline

The pipeline processes order data through three primary data layers.

### Bronze

Raw source data is uploaded to Amazon S3 using date-based partitioning:

```text
bronze/orders/
└── ingestion_date=YYYY-MM-DD/
    └── orders_with_errors.csv
```

### Silver

Orders are validated and separated into:

```text
silver/orders/orders_valid.csv
quarantine/orders/orders_invalid.csv
```

Validation currently checks for:

* Duplicate order IDs
* Missing customer IDs
* Invalid quantities
* Invalid order dates
* Missing unit prices

### Gold

Validated orders are transformed into an analytical sales dataset:

```text
gold/sales/daily_product_sales.csv
```

The dataset contains:

* Order date
* Product ID
* Total orders
* Total quantity
* Total sales

## Data Quality

Dagster asset checks are used to verify the Silver dataset.

Current checks include:

* No validation errors
* Unique order IDs
* Positive quantities
* Valid unit prices

Invalid source records are quarantined rather than silently discarded.

## AI Data Quality Analysis

Amazon Bedrock is integrated into the data quality workflow.

The deterministic Python validation layer identifies data-quality problems, while the AI layer provides human-readable analysis and recommendations.

This separation keeps the pipeline deterministic while using AI where it adds value.

Example:

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

GitHub Actions automatically runs the test suite on pushes and pull requests.

## CI/CD and AWS Pipeline Execution

The project includes a manual GitHub Actions workflow that runs the full Python data pipeline against AWS.

The workflow uses GitHub OpenID Connect to assume an AWS IAM role, so no long-lived AWS access keys are stored in GitHub.

The manual pipeline workflow:

* Checks out the repository
* Installs Python dependencies
* Assumes the AWS GitHub Actions IAM role using OIDC
* Verifies AWS identity
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

## Key Engineering Practices Demonstrated

This project is designed to demonstrate practical data engineering skills including:

* Python application development
* ETL/ELT pipeline design
* Cloud object storage
* Data lake architecture
* Data quality engineering
* Data validation and quarantine
* Pipeline orchestration
* Automated testing
* CI/CD
* Secure GitHub Actions to AWS authentication using OIDC
* AI/LLM integration
* Infrastructure as code
* AWS IAM and security
* Reproducible infrastructure

## Recent Progress

### Manual GitHub Actions pipeline run

Added a manual GitHub Actions workflow that runs the full Python data pipeline against AWS using OpenID Connect authentication.

The workflow:

* Assumes an AWS IAM role without storing long-lived AWS credentials in GitHub
* Runs the pipeline from GitHub Actions
* Writes raw source data to the Bronze S3 layer
* Validates orders into Silver and Quarantine outputs
* Builds a Gold daily product sales summary

Verified outputs:

```text
bronze/orders/ingestion_date=YYYY-MM-DD/orders_with_errors.csv
silver/orders/orders_valid.csv
quarantine/orders/orders_invalid.csv
gold/sales/daily_product_sales.csv
```

## Future Improvements

Planned improvements include:

* Additional data sources
* More comprehensive data quality checks
* Production-style configuration management
* Monitoring and alerting
* Data visualisation
* Additional AWS services
* Improved AI-generated data quality reporting
* Terraform validation workflow in CI

## Project Goals

The goal of this project is to demonstrate the design and implementation of a realistic cloud-based data engineering platform while applying software engineering principles such as testing, automation, orchestration, infrastructure as code, and maintainable Python development.
