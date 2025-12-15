from pydantic import BaseModel, Field
from enum import Enum


class PaymentTypeEnum(str, Enum):
    cash = "cash"
    bank_card = "bank-card"
    e_money = "e-money"
    bank_transfer = "bank-transfer"
    credit = "credit"


class PaymentStatusEnum(str, Enum):
    not_paid = ("not-paid",)
    invoice = ("invoice",)
    wait_approved = ("wait-approved",)
    payment_start = ("payment-start",)
    canceled = ("canceled",)
    fail = ("fail",)
    paid = ("paid",)
    returned = "returned"


class PaymentCreateSchema(BaseModel):
    order_id: int
    amount: float
    type: PaymentTypeEnum = Field(default=PaymentTypeEnum.cash)
    status: PaymentStatusEnum = Field(default=PaymentStatusEnum.not_paid)
    paid_at: str | None = Field(default=None, alias="paidAt")
    comment: str | None = None
    model_config = {"populate_by_name": True}


class PaymentResponseSchema(BaseModel):
    id: int
