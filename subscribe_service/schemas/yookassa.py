from schemas.base import Model


class Amount(Model):
    value: str
    currency: str = "RUB"


class Confirmation(Model):
    type: str = "redirect"
    return_url: str


class YookassaPayment(Model):
    amount: Amount
    confirmation: Confirmation
    capture: bool = True
    description: str


class YookassaRefund(Model):
    amount: Amount
    payment_id: str
