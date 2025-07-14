from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    PROCESSING = 'processing'

class Type_status_enum(str, Enum):
    PIX = 'pix'
    CREDIT_CARD = 'credit_card' 
    DEBIT_CARD = 'debit_card'
    CASH = 'cash'
    BOLETO = 'boleto'
    WALLET = 'wallet'

class Transaction_type(str, Enum):
    RIDE_PAYMENT = 'ride_payment'
    DRIVER_PAYMENT = 'driver_payment'
    WALLET_RECHARGE = 'wallet_recharge'
    REFUND = 'refund'

class Currency(str, Enum):
    BRL = 'brl'
    USD = 'usd'
    EUR = 'eur'
