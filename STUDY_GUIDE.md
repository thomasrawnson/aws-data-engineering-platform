# AWS Data Engineering Platform Study Guide

This guide is a companion to the project README. It is intended to help explain the project clearly in interviews, remember why key technologies were used, and revise the main engineering decisions.

## 1. Project elevator pitch

This project is an end-to-end AWS data engineering platform for processing order data.

It ingests raw CSV order files, stores them in a Bronze S3 layer, validates the data, separates valid and invalid records into Silver and Quarantine layers, builds a Gold analytical sales summary, and uses Amazon Bedrock to produce AI-assisted data quality recommendations. The project is tested with Pytest, orchestrated with Dagster, deployed through GitHub Actions, and supported by Terraform-managed AWS infrastructure.

A concise interview version:

> I built a Python-based AWS data engineering platform that demonstrates ingestion, validation, quarantine handling, analytical transformation, orchestration, CI/CD, infrastructure as code, and secure GitHub-to-AWS authentication using OIDC.

## 2. What problem the project solves

The project models a common data engineering problem: raw operational data arrives in files, but it cannot be trusted immediately for analytics.

The platform addresses this by:

- preserving raw source data in Bronze
- validating records before they reach the clean data layer
- quarantining bad records instead of silently dropping them
- producing an analytical Gold dataset for reporting
- adding automated tests and CI checks so changes are safer
- managing cloud infrastructure through Terraform
- avoiding long-lived AWS keys in GitHub by using OIDC

## 3. Architecture summary

The main flow is:

```text
Source CSV orders
    -> Bronze S3 raw storage
    -> Python validation
    -> Silver valid orders
    -> Quarantine invalid orders
    -> Gold daily product sales summary
    -> AI-assisted quality report
```

The GitHub Actions pipeline can also run the project remotely:

```text
GitHub Actions
    -> GitHub OIDC token
    -> AWS IAM role assumption
    -> Python pipeline execution
    -> S3 Bronze / Silver / Quarantine / Gold outputs
```

## 4. Why Python was used

Python was used because it is widely used in data engineering for ingestion, validation, transformation, automation, and orchestration.

In this project, Python is responsible for:

- reading source order data
- creating Bronze S3 keys
- validating data quality rules
- splitting valid and invalid records
- building Gold sales aggregates
- writing DataFrames to S3
- integrating with Amazon Bedrock
- supporting unit tests with Pytest

Interview explanation:

> I used Python because it is practical for building data pipelines and because it lets me demonstrate modular data engineering code, tests, cloud SDK usage, and orchestration-friendly functions.

## 5. Why Pandas was used

Pandas was used for DataFrame-based transformations on small sample datasets.

It is suitable here because:

- the project is a portfolio-scale pipeline, not a high-volume distributed system
- it makes validation and aggregation logic clear
- it keeps the focus on pipeline design, testing, and AWS integration
- it is easy to test with small in-memory DataFrames

Important limitation:

> Pandas is not the right tool for every data scale. For large datasets, a future version could use Spark, AWS Glue, Athena, or a warehouse-based transformation pattern.

Interview explanation:

> I chose Pandas because the project demonstrates pipeline structure and data quality logic on manageable sample data. If the dataset became large, I would move the transformation layer to Spark, Glue, Athena, or another scalable processing service.

## 6. Why AWS S3 was used

Amazon S3 was used as the data lake storage layer.

S3 is useful in data engineering because it is:

- durable object storage
- suitable for raw and processed data zones
- cost-effective for file-based data lakes
- commonly used with AWS analytics services
- easy to integrate with Python using boto3

In this project, S3 stores:

```text
bronze/orders/...
silver/orders/orders_valid.csv
quarantine/orders/orders_invalid.csv
gold/sales/daily_product_sales.csv
```

Interview explanation:

> I used S3 because it is a standard AWS data lake storage service. It allowed me to model Bronze, Silver, Quarantine, and Gold layers in a simple but realistic way.

## 7. Why Bronze, Silver, Quarantine, and Gold layers were used

The layered design separates data by quality and purpose.

### Bronze

Bronze stores raw source data as received.

Reason:

- preserves the original input
- supports reprocessing if validation rules change
- provides an audit trail of source data

### Silver

Silver stores clean, validated records.

Reason:

- downstream transformations should use trusted data
- validation metadata is removed from clean business data
- the layer is closer to analytics-ready data

### Quarantine

Quarantine stores invalid records with validation errors.

Reason:

- bad data should not silently disappear
- data quality issues can be reviewed and fixed
- invalid records remain available for reporting and investigation

### Gold

Gold stores analytical outputs.

Reason:

- creates business-facing datasets
- supports reporting and dashboard use cases
- separates raw processing from analytical modelling

Interview explanation:

> I used the layered approach to show how raw data can be preserved, validated, separated, and transformed into analytics-ready outputs. The Quarantine layer is important because invalid data should be visible and explainable, not silently removed.

## 8. Why validation rules were added

Validation rules were added to stop poor-quality records from reaching analytical outputs.

Current validation checks include:

- duplicate order IDs
- missing customer IDs
- invalid quantities
- invalid order dates
- missing unit prices

These checks matter because they protect the Gold output. For example, invalid quantities or missing prices would distort sales totals.

Interview explanation:

> I added deterministic validation rules before the Silver layer so that downstream analytics are built only from trusted records. Invalid records are retained in Quarantine with clear validation errors.

## 9. Why invalid records are quarantined rather than deleted

Quarantine is used because deleting invalid records loses information.

Quarantine supports:

- auditability
- debugging
- data quality reporting
- source-system feedback
- future reprocessing

Interview explanation:

> I quarantined invalid records because data engineering pipelines should make quality problems visible. Dropping bad records may hide source issues and make reconciliation harder.

## 10. Why Dagster was used

Dagster was used for orchestration.

It helps model the pipeline as assets and checks rather than as one large script.

In this project, Dagster provides:

- asset-based pipeline structure
- clear dependencies between Bronze, Silver, Gold, and quality reporting
- asset checks for data quality
- scheduled pipeline execution
- a visual way to inspect pipeline flow

Interview explanation:

> I used Dagster because it lets me model pipeline outputs as assets and attach checks to those assets. That makes the data flow easier to reason about than a single script and demonstrates orchestration thinking.

## 11. Why Pytest was used

Pytest was used for automated testing.

Tests currently cover:

- Bronze key creation
- validation rule behaviour
- Silver transformation expectations
- Gold aggregation logic
- AI quality analysis logic
- quality report generation

Testing matters because data pipelines can fail silently if transformation logic changes unexpectedly.

Interview explanation:

> I used Pytest to make the pipeline safer to change. The tests prove the main transformation and validation logic works before changes are pushed or deployed.

## 12. Why GitHub Actions was used

GitHub Actions was used for CI/CD automation.

The project uses GitHub Actions for:

- running tests on push and pull request
- checking Terraform formatting and validation
- manually running the full data pipeline in AWS

This demonstrates that the project is not just local code. It can be tested and executed through an automated workflow.

Interview explanation:

> I used GitHub Actions to show CI/CD discipline. Tests run automatically, Terraform is validated automatically, and the pipeline can be triggered manually from GitHub.

## 13. Why GitHub OIDC was used instead of AWS access keys

GitHub OIDC allows GitHub Actions to authenticate to AWS without storing permanent AWS access keys in GitHub secrets.

The workflow is:

```text
GitHub Actions job
    -> receives an OIDC identity token
    -> presents token to AWS STS
    -> assumes an IAM role
    -> receives temporary credentials
```

Reasons this is better than long-lived keys:

- no static AWS credentials stored in GitHub
- temporary credentials are issued only when the workflow runs
- AWS IAM trust policy can restrict which repository and branch can assume the role
- easier to rotate and manage securely

Interview explanation:

> I used GitHub OIDC because it is a more secure authentication pattern than storing long-lived AWS keys. The IAM trust policy restricts role assumption to my repository and main branch.

## 14. Why Terraform was used

Terraform was used to manage infrastructure as code.

It manages:

- the existing S3 data lake bucket
- S3 public access blocking
- S3 server-side encryption
- S3 versioning
- S3 ownership controls
- the GitHub OIDC provider
- the GitHub Actions IAM role
- IAM policies for S3 and Bedrock access

Benefits:

- infrastructure is version controlled
- changes can be reviewed before applying
- `terraform plan` shows intended changes
- infrastructure can be reproduced more reliably
- manual console changes can be detected as drift

Interview explanation:

> I used Terraform so the AWS infrastructure is documented, repeatable, and reviewable. It also lets me detect differences between the code and the real AWS environment.

## 15. Why Terraform imported the existing S3 bucket

The S3 bucket already existed before Terraform was added.

Rather than deleting and recreating it, the bucket was imported into Terraform state.

Reason:

- preserves existing data
- avoids unnecessary infrastructure recreation
- brings existing cloud resources under code management
- mirrors a realistic workplace scenario where infrastructure often predates Terraform

Interview explanation:

> I imported the existing S3 bucket because the data lake already existed. Importing let me bring it under Terraform control without deleting or recreating the bucket.

## 16. Why S3 security settings were added

The S3 bucket is configured with:

- public access blocking
- server-side encryption
- versioning
- bucket-owner-enforced ownership controls

Reasons:

- public access blocking reduces accidental data exposure risk
- encryption protects stored data
- versioning provides recovery options if objects are overwritten or deleted
- ownership controls simplify object ownership and ACL behaviour

Interview explanation:

> I added S3 hardening settings to show that the data lake is not just functional but also configured with basic cloud security practices.

## 17. Why Amazon Bedrock was used

Amazon Bedrock was used to add AI-assisted quality analysis.

The important design choice is that the AI does not decide whether records are valid. Deterministic Python rules handle validation first. The AI layer is used to produce human-readable recommendations based on known validation issues.

This keeps the pipeline reliable while still showing a practical AI use case.

Interview explanation:

> I kept validation deterministic and used Bedrock only for explanation and recommendation. That avoids relying on an LLM for core data correctness while still demonstrating a practical AI enhancement.

## 18. Why deterministic validation and AI are separated

The separation matters because data correctness should be predictable and testable.

Deterministic validation is used for:

- pass/fail rules
- record classification
- repeatable results
- automated tests

AI is used for:

- summarising quality issues
- improving recommendations
- making quality reports more readable

Interview explanation:

> I separated deterministic validation from AI recommendations because core data quality decisions need to be repeatable. AI is useful for interpretation, not as the source of truth for validity.

## 19. Why a manual pipeline workflow was added

The manual workflow allows the pipeline to be run from GitHub Actions only when needed.

Reasons:

- avoids running the pipeline on every push
- prevents unnecessary AWS writes and potential Bedrock calls
- gives a controlled demonstration of CI/CD pipeline execution
- proves GitHub can authenticate to AWS and write to S3

Interview explanation:

> I made the AWS pipeline run manual because it writes to cloud storage. Tests can run automatically on every push, but full cloud pipeline execution is better controlled through manual dispatch at this stage.

## 20. Why a Terraform validation workflow was added

The Terraform workflow runs:

```text
terraform fmt -check
terraform init -backend=false
terraform validate
```

It does not run `terraform apply`.

Reasons:

- catches formatting and syntax issues early
- validates Terraform code in CI
- avoids accidental infrastructure changes
- demonstrates infrastructure quality checks without deployment risk

Interview explanation:

> I added Terraform validation in CI but avoided automatic apply. That gives fast feedback on Terraform quality without risking unintended cloud changes.

## 21. Important commands to remember

### Run tests

```bash
python -m pytest -v
```

### Run the local pipeline

```bash
python -m src.pipeline.run_pipeline
```

### Check Terraform state against AWS

```bash
terraform -chdir=terraform plan
```

### Format Terraform

```bash
terraform -chdir=terraform fmt
```

### Validate Terraform locally

```bash
terraform -chdir=terraform validate
```

### Check S3 outputs

```bash
aws s3 ls s3://tom-data-engineering-platform/bronze/orders/ --recursive
aws s3 ls s3://tom-data-engineering-platform/silver/orders/ --recursive
aws s3 ls s3://tom-data-engineering-platform/quarantine/orders/ --recursive
aws s3 ls s3://tom-data-engineering-platform/gold/sales/ --recursive
```

### Open the project in VS Code

```bash
cd ~/Documents/aws-data-engineering-platform
code .
```

## 22. Files worth knowing

### Pipeline and ingestion

- `src/pipeline/run_pipeline.py` runs the end-to-end pipeline
- `src/ingestion/ingest_orders.py` handles Bronze ingestion
- `src/utils/s3.py` contains reusable S3 helpers
- `src/utils/config.py` loads project configuration

### Validation and transformation

- `src/validation/order_validation.py` contains validation rules
- `src/validation/run_validation.py` runs validation and writes Silver/Quarantine outputs
- `src/gold/build_gold.py` builds the Gold daily sales summary

### AI layer

- `src/ai/bedrock_client.py` calls Amazon Bedrock
- `src/ai/quality_analyzer.py` builds quality insights
- `src/ai/quality_report.py` creates a quality report output

### Orchestration

- `src/dagster_project/definitions.py` defines Dagster assets, checks, and schedule

### Infrastructure and CI/CD

- `terraform/main.tf` contains S3 infrastructure
- `terraform/iam.tf` contains IAM and GitHub OIDC resources
- `.github/workflows/tests.yml` runs Python tests and AWS integration checks
- `.github/workflows/run-pipeline.yml` manually runs the full pipeline in AWS
- `.github/workflows/terraform.yml` validates Terraform code

## 23. Key interview questions and answers

### What does the project demonstrate?

It demonstrates a realistic data engineering workflow: ingestion, validation, data lake layering, quarantine handling, transformation, orchestration, testing, CI/CD, cloud infrastructure, IAM, and AI-assisted quality reporting.

### Why did you use S3 instead of a database?

S3 is a common foundation for data lakes. It is suitable for storing raw and processed files across Bronze, Silver, and Gold layers. A database or warehouse could be added later for serving analytics.

### Why not use Glue or Spark?

The project currently uses Pandas because the dataset is small and the goal is to demonstrate pipeline design, validation, testing, and AWS integration. If data volume increased, Glue or Spark would be a natural next step.

### Why use Dagster?

Dagster makes pipeline dependencies explicit through assets and checks. It provides a cleaner orchestration model than a single script and supports scheduled runs and quality checks.

### Why use Terraform?

Terraform makes the infrastructure version controlled, reviewable, and reproducible. It also allows drift detection using `terraform plan`.

### Why use GitHub OIDC?

OIDC avoids storing long-lived AWS credentials in GitHub. GitHub receives a temporary identity token and AWS exchanges it for temporary role credentials if the trust policy allows it.

### What is the purpose of Quarantine?

Quarantine keeps invalid records visible for review and reprocessing. It prevents bad records entering analytics while avoiding silent data loss.

### What is the role of Bedrock?

Bedrock is used to make data quality reporting more readable and useful. It does not decide whether data is valid; deterministic Python rules do that first.

### What would you improve next?

Likely next improvements include incremental ingestion, another data source, richer monitoring, alerting, a dashboard, or a warehouse query layer.

## 24. Things to be careful explaining

Do not say the project is production-grade. A better phrase is:

> This is a portfolio-grade project that demonstrates production-style practices on a controlled dataset.

Do not say AI validates the data. Say:

> Python validation rules classify records, and AI assists with explanations and recommendations.

Do not say Terraform created everything from scratch. Say:

> Terraform manages the infrastructure, including an existing S3 bucket that was imported into state.

Do not say GitHub stores AWS credentials. Say:

> GitHub Actions uses OIDC to assume an AWS IAM role and receive temporary credentials.

## 25. One-minute explanation

This project is an AWS data engineering platform built in Python. It ingests order CSV data into a Bronze S3 layer, validates records, writes clean data to Silver, sends invalid records to Quarantine, and builds a Gold daily product sales summary. I used Pytest to test the transformation logic, Dagster to model the pipeline as assets and checks, and Amazon Bedrock to add AI-assisted quality recommendations while keeping validation deterministic. Infrastructure is managed with Terraform, including S3 security settings, IAM, and GitHub OIDC. GitHub Actions runs tests, validates Terraform, and can manually run the full pipeline in AWS without storing long-lived AWS keys.

## 26. Thirty-second explanation

I built a Python and AWS data engineering project that takes raw order files through Bronze, Silver, Quarantine, and Gold S3 layers. It validates data quality, quarantines bad records, produces an analytical sales output, and uses Dagster, Pytest, Terraform, GitHub Actions, OIDC, and Bedrock to demonstrate modern data engineering practices.
