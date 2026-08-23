import logging
import pandas as pd
from src.utils.logging_config import configure_logging
from src.utils.s3 import upload_dataframe
from src.validation.order_validation import validate_orders


logger = logging.getLogger(__name__)


def run_validation(input_file: str) -> None:
    """Run data quality validation against an orders file."""

    logger.info("Starting validation pipeline")
    logger.info("Reading orders from %s", input_file)

    try:
        orders = pd.read_csv(input_file)

    except FileNotFoundError:
        logger.error("Input file not found: %s", input_file)
        raise

    logger.info("Records received: %d", len(orders))

    valid_orders, invalid_orders = validate_orders(orders)

    logger.info("Valid records: %d", len(valid_orders))
    logger.info("Invalid records: %d", len(invalid_orders))

    # Remove validation metadata from clean Silver data
    silver_orders = valid_orders.drop(
        columns=["validation_error"]
    )

    if len(invalid_orders) > 0:
        logger.warning(
            "Data quality issues detected: %d invalid records",
            len(invalid_orders),
        )

        for _, row in invalid_orders.iterrows():
            logger.warning(
                "Order %s: %s",
                row["order_id"],
                row["validation_error"],
            )

    # Keep the local outputs for development/testing
    silver_orders.to_csv(
        "data/processed/valid/orders_valid.csv",
        index=False,
    )

    invalid_orders.to_csv(
        "data/processed/quarantine/orders_invalid.csv",
        index=False,
    )

    # Upload Silver data to S3
    upload_dataframe(
        silver_orders,
        "silver/orders/orders_valid.csv",
    )

    # Upload invalid records to S3 Quarantine
    upload_dataframe(
        invalid_orders,
        "quarantine/orders/orders_invalid.csv",
    )

    logger.info("Validation results written successfully")

if __name__ == "__main__":
    configure_logging()

    run_validation(
        "data/sample/orders_with_errors.csv"
    )