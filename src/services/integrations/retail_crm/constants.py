from enum import StrEnum
from typing import Any
from src.core.config import settings


class RetailCRMEndpoint(StrEnum):
    CUSTOMERS_LIST = "/customers"
    CUSTOMERS_CREATE = "/customers/create"

    ORDERS_LIST = "/orders"
    ORDER_CREATE = "/orders/create"
    ORDER_GET = "/orders/{order_id}"

    PAYMENTS_CREATE = "/orders/payments/create"

    def build(self, **kwargs: Any) -> str:
        return self.value.format(**kwargs)


URL = settings.RETAIL_CRM_URL
API_KEY = settings.RETAIL_CRM_API_KEY
PREFIX = settings.RETAIL_CRM_API_PREFIX
