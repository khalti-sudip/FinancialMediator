import logging
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

# Configure logging
logger = logging.getLogger(__name__)


class TransactionSchema(Schema):
    """Schema for validating transaction requests"""
    source_system = fields.String(required=True)
    target_system = fields.String(required=True)
    transaction_type = fields.String(required=True)
    user_id = fields.String(required=False)
    transaction_id = fields.String(required=False)  # Generated if not provided
    amount = fields.Float(required=False)
    currency = fields.String(required=False, validate=validate.Length(min=3, max=3))
    payload = fields.Dict(required=False)
    params = fields.Dict(required=False)
    method = fields.String(validate=validate.OneOf(['GET', 'POST']), default='POST')
    cacheable = fields.Boolean(default=False)
    
    @validates_schema
    def validate_transaction(self, data, **kwargs):
        """Custom validation for transactions"""
        # If transaction involves money, amount and currency are required
        if data.get('transaction_type') in ['payment', 'transfer', 'withdrawal', 'deposit']:
            if 'amount' not in data or data.get('amount') is None:
                raise ValidationError('Amount is required for this transaction type')
            if 'currency' not in data or not data.get('currency'):
                raise ValidationError('Currency is required for this transaction type')


def validate_transaction_request(transaction_data):
    """
    Perform business validation on transaction data
    
    Args:
        transaction_data (dict): The transaction data to validate
    
    Returns:
        list: A list of validation error messages, empty if valid
    """
    errors = []
    
    # Validate amount if present
    if 'amount' in transaction_data and transaction_data['amount'] is not None:
        if transaction_data['amount'] <= 0:
            errors.append("Amount must be greater than zero")
    
    # Validate currency if present
    if 'currency' in transaction_data and transaction_data['currency']:
        if len(transaction_data['currency']) != 3:
            errors.append("Currency must be a 3-character ISO code")
    
    # Validate transaction types
    valid_transaction_types = [
        'payment', 'transfer', 'withdrawal', 'deposit', 
        'balance', 'account_info', 'statement', 'kyc',
        'loan_application', 'investment', 'insurance', 'test'
    ]
    
    if transaction_data.get('transaction_type') not in valid_transaction_types:
        errors.append(f"Invalid transaction type. Must be one of: {', '.join(valid_transaction_types)}")
    
    # Validate specific transaction types
    if transaction_data.get('transaction_type') == 'transfer':
        payload = transaction_data.get('payload', {})
        if not payload.get('source_account'):
            errors.append("Source account is required for transfer transactions")
        if not payload.get('destination_account'):
            errors.append("Destination account is required for transfer transactions")
    
    if transaction_data.get('transaction_type') == 'payment':
        payload = transaction_data.get('payload', {})
        if not payload.get('beneficiary'):
            errors.append("Beneficiary information is required for payment transactions")
    
    logger.debug(f"Validation results for transaction: {errors if errors else 'Valid'}")
    return errors


class UserSchema(Schema):
    """Schema for validating user data in transactions"""
    id = fields.String(required=True)
    name = fields.String(required=False)
    email = fields.Email(required=False)
    phone = fields.String(required=False)


class AccountSchema(Schema):
    """Schema for validating account data in transactions"""
    account_number = fields.String(required=True)
    account_type = fields.String(required=False)
    currency = fields.String(required=False, validate=validate.Length(min=3, max=3))
    bank_code = fields.String(required=False)


class BeneficiarySchema(Schema):
    """Schema for validating beneficiary data in transactions"""
    name = fields.String(required=True)
    account_number = fields.String(required=True)
    bank_code = fields.String(required=True)
    bank_name = fields.String(required=False)
    swift_code = fields.String(required=False)
    iban = fields.String(required=False)
    address = fields.String(required=False)
    country = fields.String(required=False)
    reference = fields.String(required=False)


class PaymentSchema(Schema):
    """Schema for validating payment transaction data"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    currency = fields.String(required=True, validate=validate.Length(min=3, max=3))
    beneficiary = fields.Nested(BeneficiarySchema, required=True)
    source_account = fields.String(required=True)
    payment_details = fields.String(required=False)
    payment_type = fields.String(required=False)
    execution_date = fields.Date(required=False)
    reference = fields.String(required=False)


class TransferSchema(Schema):
    """Schema for validating transfer transaction data"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    currency = fields.String(required=True, validate=validate.Length(min=3, max=3))
    source_account = fields.String(required=True)
    destination_account = fields.String(required=True)
    transfer_details = fields.String(required=False)
    reference = fields.String(required=False)


class BalanceSchema(Schema):
    """Schema for validating balance inquiry transaction data"""
    account_number = fields.String(required=True)
    include_pending = fields.Boolean(default=False)
    currency = fields.String(required=False, validate=validate.Length(min=3, max=3))
