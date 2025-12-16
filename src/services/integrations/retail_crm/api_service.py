from typing import Optional, Dict, Any
import json
from pydantic import BaseModel
from src.core.logger import get_logger
from src.services.integrations.base_crm import BaseCRMService
from src.schemas.customers import (
    CustomerFiltersSchema,
    CustomerGetSchema,
    CustomerAddSchema,
    CustomerResponseWithIdOnlySchema,
    CustomerGetOrdersSchema,
    CustomersListResponseSchema,
)
from src.schemas.orders import (
    OrdersListResponse,
    OrderCreateSchema,
    OrderResponseSchema,
)
from src.schemas.payments import PaymentCreateSchema, PaymentResponseSchema
from src.services.integrations.retail_crm.constants import (
    RetailCRMEndpoint as E,
    API_KEY,
    URL,
    PREFIX,
)
from src.services.integrations.constants_base import HTTPMethod

logger = get_logger("retailcrm_service")


class RetailCRMService(BaseCRMService):
    """
    Realization of base service for work with RetailCRM API.
    """

    def __init__(self):
        self.api_key = API_KEY
        super().__init__(api_url=URL + PREFIX, timeout=30.0)
        logger.debug(f"RetailCRMService initialized with API URL: {self.api_url}")

    def _prepare_request_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Preparing request parameters (query params) for RetailCRM.
        Adding API key to the request parameters.
        """
        request_params = params.copy() if params else {}
        request_params["apiKey"] = self.api_key
        return request_params

    def _prepare_request_body(self, json_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Preparing request body (JSON) for RetailCRM.
        """
        return json_data

    def _prepare_request_headers(
        self,
        headers: Optional[Dict[str, Any]] = None,
        method: str = HTTPMethod.POST,
    ) -> Optional[Dict[str, Any]]:
        """
        Preparing request headers for RetailCRM.
        """
        if headers is None:
            headers = {}
        if method == HTTPMethod.POST:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    def _validate_response(self, response: Dict[str, Any], endpoint: str) -> None:
        """
        Response validation for RetailCRM API.
        Checks response field 'success' and throws an exception if it is False.
        """
        if not response.get("success", False):
            error_msg = response.get("errorMsg", "Unknown error")
            logger.error(
                f"RetailCRM API returned error: {error_msg}",
                extra={
                    "endpoint": endpoint,
                    "error_msg": error_msg,
                    "response": response,
                },
            )
            raise Exception(f"RetailCRM API error: {error_msg}")

    def _convert_filter_data_to_retail_crm_style(self, filter_dto: BaseModel | dict) -> Dict[str, Any]:
        """
        Converts filters into RetailCRM GET parameter format.
        Supports nested dictionaries and lists.
        """
        if not isinstance(filter_dto, dict):
            filters = filter_dto.model_dump(exclude_none=True, by_alias=True)
        else:
            filters = {k: v for k, v in filter_dto.items() if v is not None}

        params: dict[str, Any] = {}
        filter_dict = {}

        for key, value in filters.items():
            if key in ("limit", "page"):
                params[key] = value
            else:
                filter_dict[key] = value

        def flatten(prefix: str, value: Any):
            if isinstance(value, dict):
                for k, v in value.items():
                    flatten(f"{prefix}[{k}]", v)
            elif isinstance(value, list):
                for item in value:
                    flatten(f"{prefix}[]", item)
            else:
                params[f"{prefix}"] = value

        for k, v in filter_dict.items():
            flatten(f"filter[{k}]", v)

        return params

    async def get_customers(self, filter_dto: CustomerFiltersSchema) -> CustomersListResponseSchema:
        """Obtaining a filtered list of customers"""
        logger.info(
            "Getting customers list",
            extra={
                "name_filter": filter_dto.name,
                "email_filter": filter_dto.email,
                "created_at_from": filter_dto.created_at_from,
                "created_at_to": filter_dto.created_at_to,
                "limit": filter_dto.limit,
                "page": filter_dto.page,
            },
        )
        params = {"limit": filter_dto.limit, "page": filter_dto.page}
        filters = self._convert_filter_data_to_retail_crm_style(filter_dto)
        params.update(filters)

        result = await self._make_request(HTTPMethod.GET, E.CUSTOMERS_LIST, params=params)

        customers = [CustomerGetSchema(**customer) for customer in result.get("customers", [])]

        customers_count = len(customers)
        logger.info(f"Retrieved {customers_count} customers")

        return CustomersListResponseSchema(customers=customers, pagination=result.get("pagination"))

    async def create_customer(self, customer_dto: CustomerAddSchema) -> CustomerResponseWithIdOnlySchema:
        """Creating new customer"""
        logger.info(
            "Creating new customer",
            extra={
                "first_name": customer_dto.first_name,
                "email": customer_dto.email,
                "has_phones": bool(customer_dto.phones),
            },
        )
        customer_data = customer_dto.model_dump(exclude_none=True, by_alias=True)
        result = await self._make_request(
            HTTPMethod.POST,
            E.CUSTOMERS_CREATE,
            json_data={"customer": json.dumps(customer_data)},
        )

        # RetailCRM возвращает данные в поле "customer" или напрямую
        customer_data_response = result.get("customer") or result
        customer_response = CustomerResponseWithIdOnlySchema(**customer_data_response)

        if customer_response.id:
            logger.info(f"Customer created successfully with ID: {customer_response.id}")
        else:
            logger.warning("Customer creation response doesn't contain ID")

        return customer_response

    async def get_customer_orders(self, customer_data: CustomerGetOrdersSchema) -> OrdersListResponse:
        """Get list of orders for customer"""
        params = {"limit": customer_data.limit, "page": customer_data.page}
        filters = self._convert_filter_data_to_retail_crm_style(customer_data)
        params.update(filters)
        logger.info(f"Getting orders for customer ID: {customer_data.customer_id}", extra=params)
        result = await self._make_request(HTTPMethod.GET, E.ORDERS_LIST, params=params)

        orders = [OrderResponseSchema(**order) for order in result.get("orders", [])]

        orders_count = len(orders)
        logger.info(f"Retrieved {orders_count} orders for customer {customer_data.customer_id}")

        return OrdersListResponse(orders=orders, pagination=result.get("pagination"))

    async def create_order(self, order_dto: OrderCreateSchema) -> OrderResponseSchema:
        """Creating new order in CRM"""
        order_number = order_dto.number
        customer_id = order_dto.customer.id
        items_count = len(order_dto.items)

        logger.info(
            "Creating new order",
            extra={
                "order_number": order_number,
                "customer_id": customer_id,
                "items_count": items_count,
            },
        )
        order_data = order_dto.model_dump(exclude_none=True, by_alias=True)
        result = await self._make_request(HTTPMethod.POST, E.ORDER_CREATE, json_data={"order": json.dumps(order_data)})
        order_data_response = result.get("order") or result
        order_response = OrderResponseSchema(**order_data_response)
        if order_response.id:
            logger.info(f"Order created successfully with ID: {order_response.id}, number: {order_number}")
        else:
            logger.warning("Order creation response doesn't contain ID")
        return order_response

    async def create_payment(self, payment_dto: PaymentCreateSchema) -> PaymentResponseSchema:
        """Creating new payment in CRM"""
        order_id = payment_dto.order_id
        amount = payment_dto.amount
        payment_type = payment_dto.type
        logger.info(
            f"Creating payment for order ID: {order_id}",
            extra={
                "order_id": order_id,
                "amount": amount,
                "payment_type": payment_type,
            },
        )
        logger.debug(f"Checking if order {order_id} exists")
        order_response = await self._make_request(
            HTTPMethod.GET, E.ORDER_GET.build(order_id=order_id), params={"by": "id"}
        )
        if not order_response.get("success") or not order_response.get("order"):
            logger.error(f"Order with id {order_id} not found")
            raise Exception(f"Order with id {order_id} not found")
        logger.debug(f"Order {order_id} found, proceeding with payment creation")
        payment_data = payment_dto.model_dump(exclude_none=True, exclude={"order_id"})
        payment_data["order"] = {"id": order_id}
        result = await self._make_request(
            HTTPMethod.POST,
            E.PAYMENTS_CREATE,
            json_data={"payment": json.dumps(payment_data)},
        )
        payment_data_response = result.get("payment") or result
        payment_response = PaymentResponseSchema(**payment_data_response)
        if payment_response.id:
            logger.info(f"Payment created successfully with ID: {payment_response.id} for order {order_id}")
        else:
            logger.warning("Payment creation response doesn't contain ID")
        return payment_response
