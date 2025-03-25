import logging
import copy
import json
import datetime

# Configure logging
logger = logging.getLogger(__name__)


def transform_request(request_data, source_system, target_system):
    """
    Transform a request from the source system format to the target system format

    Args:
        request_data (dict): The original request data
        source_system (SystemConfig): The source system configuration
        target_system (SystemConfig): The target system configuration

    Returns:
        dict: The transformed request data
    """
    logger.debug(
        f"Transforming request from {source_system.system_name} to {target_system.system_name}"
    )

    # Create a deep copy to avoid modifying the original
    transformed_data = copy.deepcopy(request_data)

    # Get transaction type to determine transformation rules
    transaction_type = request_data.get("transaction_type", "")

    # Apply common transformations
    transformed_data["source"] = source_system.system_name
    transformed_data["timestamp"] = datetime.datetime.utcnow().isoformat()

    # Apply specific transformations based on source and target systems
    if target_system.system_type == "financial_provider":
        transformed_data = transform_to_provider_format(
            transformed_data, transaction_type
        )
    elif target_system.system_type == "banking_system":
        transformed_data = transform_to_banking_format(
            transformed_data, transaction_type
        )

    logger.debug(f"Request transformation completed for {transaction_type}")
    return transformed_data


def transform_response(response_data, source_system, target_system):
    """
    Transform a response from the source system format to the target system format

    Args:
        response_data (dict): The original response data
        source_system (SystemConfig): The source system configuration
        target_system (SystemConfig): The target system configuration

    Returns:
        dict: The transformed response data
    """
    logger.debug(
        f"Transforming response from {source_system.system_name} to {target_system.system_name}"
    )

    # Create a deep copy to avoid modifying the original
    transformed_data = copy.deepcopy(response_data)

    # Add middleware metadata
    transformed_data["processed_by"] = "banking_middleware"
    transformed_data["processed_at"] = datetime.datetime.utcnow().isoformat()

    # Apply specific transformations based on source and target systems
    if (
        source_system.system_type == "financial_provider"
        and target_system.system_type == "banking_system"
    ):
        transformed_data = transform_provider_to_banking_response(transformed_data)
    elif (
        source_system.system_type == "banking_system"
        and target_system.system_type == "financial_provider"
    ):
        transformed_data = transform_banking_to_provider_response(transformed_data)

    logger.debug("Response transformation completed")
    return transformed_data


def transform_to_provider_format(data, transaction_type):
    """
    Transform data to a financial service provider format

    Args:
        data (dict): The data to transform
        transaction_type (str): The type of transaction

    Returns:
        dict: The transformed data
    """
    transformed = copy.deepcopy(data)

    # Map common fields to provider expected format
    if "payload" not in transformed:
        transformed["payload"] = {}

    # Format specific transformations
    if transaction_type == "payment":
        # Extract payment details from the payload
        payment = transformed.get("payload", {})

        # Create a properly formatted payment request
        transformed["payload"] = {
            "paymentRequest": {
                "amount": {
                    "value": str(transformed.get("amount", 0)),
                    "currency": transformed.get("currency", "USD"),
                },
                "beneficiary": {
                    "name": payment.get("beneficiary", {}).get("name", ""),
                    "accountNumber": payment.get("beneficiary", {}).get(
                        "account_number", ""
                    ),
                    "bankDetails": {
                        "bankCode": payment.get("beneficiary", {}).get("bank_code", ""),
                        "bankName": payment.get("beneficiary", {}).get("bank_name", ""),
                        "swiftCode": payment.get("beneficiary", {}).get(
                            "swift_code", ""
                        ),
                        "country": payment.get("beneficiary", {}).get("country", ""),
                    },
                },
                "sourceAccount": payment.get("source_account", ""),
                "reference": payment.get("reference", ""),
                "executionDate": payment.get(
                    "execution_date", datetime.date.today().isoformat()
                ),
            }
        }

    elif transaction_type == "balance":
        # Format balance inquiry request
        transformed["payload"] = {
            "balanceRequest": {
                "accountNumber": transformed.get("payload", {}).get(
                    "account_number", ""
                ),
                "includePending": transformed.get("payload", {}).get(
                    "include_pending", False
                ),
            }
        }

    # Add any additional metadata expected by the provider
    transformed["clientId"] = transformed.get("user_id", "")
    transformed["requestId"] = transformed.get("transaction_id", "")

    return transformed


def transform_to_banking_format(data, transaction_type):
    """
    Transform data to a banking system format

    Args:
        data (dict): The data to transform
        transaction_type (str): The type of transaction

    Returns:
        dict: The transformed data
    """
    transformed = copy.deepcopy(data)

    # Map common fields to banking system expected format
    if "payload" not in transformed:
        transformed["payload"] = {}

    # Format specific transformations
    if transaction_type == "payment":
        # Extract payment details from the payload
        payment = transformed.get("payload", {})

        # Create a properly formatted payment request for banking system
        transformed["payload"] = {
            "transaction": {
                "type": "PAYMENT",
                "amount": transformed.get("amount", 0),
                "currencyCode": transformed.get("currency", "USD"),
                "debitAccount": payment.get("source_account", ""),
                "beneficiary": {
                    "name": payment.get("beneficiary", {}).get("name", ""),
                    "accountNumber": payment.get("beneficiary", {}).get(
                        "account_number", ""
                    ),
                    "bankCode": payment.get("beneficiary", {}).get("bank_code", ""),
                    "swiftCode": payment.get("beneficiary", {}).get("swift_code", ""),
                },
                "description": payment.get("payment_details", ""),
                "reference": payment.get("reference", ""),
            }
        }

    elif transaction_type == "balance":
        # Format balance inquiry request for banking system
        transformed["payload"] = {
            "inquiry": {
                "type": "BALANCE",
                "accountNumber": transformed.get("payload", {}).get(
                    "account_number", ""
                ),
                "options": {
                    "includePendingTransactions": transformed.get("payload", {}).get(
                        "include_pending", False
                    )
                },
            }
        }

    # Add any additional metadata expected by the banking system
    transformed["customerId"] = transformed.get("user_id", "")
    transformed["externalReferenceId"] = transformed.get("transaction_id", "")

    return transformed


def transform_provider_to_banking_response(data):
    """
    Transform a response from a financial provider to banking system format

    Args:
        data (dict): The response data from the provider

    Returns:
        dict: The transformed response data
    """
    transformed = copy.deepcopy(data)

    # Handle different response structures
    if "paymentResponse" in transformed:
        payment_response = transformed.get("paymentResponse", {})

        # Transform to banking system format
        transformed = {
            "status": payment_response.get("status", "UNKNOWN"),
            "transactionId": payment_response.get("providerTransactionId", ""),
            "result": {
                "success": payment_response.get("status") == "COMPLETED",
                "message": payment_response.get("statusDescription", ""),
            },
            "details": {
                "processedAt": payment_response.get("processedAt", ""),
                "fee": payment_response.get("fee", {}),
            },
        }

    elif "balanceResponse" in transformed:
        balance_response = transformed.get("balanceResponse", {})

        # Transform to banking system format
        transformed = {
            "accountInfo": {
                "accountNumber": balance_response.get("accountNumber", ""),
                "balance": {
                    "available": balance_response.get("availableBalance", 0),
                    "current": balance_response.get("currentBalance", 0),
                    "currency": balance_response.get("currency", "USD"),
                },
                "pendingTransactions": balance_response.get("pendingTransactions", []),
            }
        }

    return transformed


def transform_banking_to_provider_response(data):
    """
    Transform a response from a banking system to provider format

    Args:
        data (dict): The response data from the banking system

    Returns:
        dict: The transformed response data
    """
    transformed = copy.deepcopy(data)

    # Handle different response structures
    if "transaction" in transformed:
        transaction = transformed.get("transaction", {})

        # Transform to provider format
        transformed = {
            "status": (
                "SUCCESS" if transaction.get("status") == "COMPLETED" else "FAILED"
            ),
            "resultCode": "00" if transaction.get("status") == "COMPLETED" else "01",
            "resultMessage": transaction.get("statusDescription", ""),
            "transactionDetails": {
                "id": transaction.get("id", ""),
                "type": transaction.get("type", ""),
                "timestamp": transaction.get("timestamp", ""),
                "amount": transaction.get("amount", 0),
                "currency": transaction.get("currency", "USD"),
            },
        }

    elif "accountInfo" in transformed:
        account_info = transformed.get("accountInfo", {})

        # Transform to provider format
        transformed = {
            "account": {
                "number": account_info.get("accountNumber", ""),
                "balances": {
                    "available": account_info.get("balance", {}).get("available", 0),
                    "current": account_info.get("balance", {}).get("current", 0),
                },
                "currency": account_info.get("balance", {}).get("currency", "USD"),
            }
        }

    return transformed
