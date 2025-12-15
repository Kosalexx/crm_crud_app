from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from src.core.logger import get_logger
from src.schemas.customers import (
    CustomerFiltersSchema,
    CustomerAddSchema,
    CustomerGetOrdersSchema,
    CustomerResponseWithIdOnlySchema,
    CustomersListResponseSchema,
)
from src.schemas.orders import (
    OrdersListResponse,
    OrderCreateSchema,
    OrderResponseSchema,
)
from src.schemas.payments import PaymentCreateSchema, PaymentResponseSchema


logger = get_logger("base_crm")


class BaseCRMService(ABC):
    """
    Abstract BaseCRMService class for interacting with CRM systems.

    This class defines a common interface for working with CRM systems.
    Contains common logic for making HTTP requests and validating responses.
    Concrete implementations should inherit from this class and implement
    """

    def __init__(self, api_url: str, timeout: float = 30.0):
        """
        Initialization of BaseCRMService.
        Args:
            api_url: Base URL API CRM system
            timeout: Timeout for HTTP requests in seconds
        """
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.debug(f"BaseCRMService initialized with API URL: {self.api_url}")

    async def close(self) -> None:
        """
        Closing connection with CRM system.
        Should be called when the application is shutting down.
        """
        await self.client.aclose()

    @abstractmethod
    def _prepare_request_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Preparing request parameters (query params).
        Should be overridden in concrete implementations. (adding API key, authentication, etc.)
        Args:
            params: Initial request parameters
        Returns:
            Prepared request parameters
        """
        pass

    @abstractmethod
    def _prepare_request_body(self, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any] | str | None:
        """
        Preparing request body (JSON).
        Should be overridden in concrete implementations.
        Args:
            json_data: Initial request body
        Returns:
            Prepared request body or None if not needed
        """
        pass

    @abstractmethod
    def _prepare_request_headers(self, headers: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Preparing request headers.
        Should be overridden in concrete implementations.
        Args:
            headers: Initial request headers
        Returns:
            Prepared request headers or None if not needed
        """
        pass

    @abstractmethod
    def _validate_response(self, response: Dict[str, Any], endpoint: str) -> None:
        """
        Validating response from CRM API.
        Should be overridden in concrete implementations for different CRM systems.

        Args:
            response: response from CRM API
            endpoint: endpoint
        Raises:
            Exception: If response is not valid
        """
        pass

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Base method for making HTTP requests to CRM API.
        Uses common logic for preparing request parameters and validating response.
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: query params
            json_data: request body
            headers: request headers

        Returns:
            Response from CRM API
        Raises:
            Exception: exception
        """
        request_params = self._prepare_request_params(params)
        request_body = self._prepare_request_body(json_data)
        headers = self._prepare_request_headers(headers)
        url = f"{self.api_url}{endpoint}"
        logger.debug(
            f"Making {method} request to CRM API",
            extra={
                "method": method,
                "endpoint": endpoint,
                "url": url,
                "params": request_params if bool(request_params) else False,
                "json": request_body if bool(request_body) else False,
                "headers": headers if bool(headers) else False,
            },
        )
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=request_params,
                data=request_body,
                headers=headers,
            )
            response.raise_for_status()
            result: dict = response.json()
            self._validate_response(result, endpoint)
            logger.debug(
                f"Successfully completed {method} request to {endpoint}",
                extra={"method": method, "endpoint": endpoint, "result": result},
            )
            return result
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(
                f"HTTP error in CRM API request: {error_detail}",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": e.response.status_code,
                    "error": error_detail,
                },
                exc_info=True,
            )
            raise Exception(f"CRM API error: {error_detail}")
        except Exception as e:
            logger.error(
                f"Request error: {str(e)}",
                extra={"method": method, "endpoint": endpoint, "error": str(e)},
                exc_info=True,
            )
            raise Exception(f"Request error: {str(e)}")

    @abstractmethod
    async def get_customers(self, customer_filters: CustomerFiltersSchema) -> CustomersListResponseSchema:
        """
        Get list of customers with optional filters.
        Args:
            customer_filters: CustomerFiltersSchema
        Returns:
            DTO with customers data
        """
        pass

    @abstractmethod
    async def create_customer(self, customer_data: CustomerAddSchema) -> CustomerResponseWithIdOnlySchema:
        """
        Creating new customer in CRM.
        Args:
            customer_data: CustomerAddSchema
        Returns:
            DTO with customer data
        """
        pass

    @abstractmethod
    async def get_customer_orders(self, customer_data: CustomerGetOrdersSchema) -> OrdersListResponse:
        """
        Get list of orders for customer.

        Args:
            customer_data: CustomerGetOrdersSchema

        Returns:
            OrdersListResponse - DTO with orders data
        """
        pass

    @abstractmethod
    async def create_order(self, order_dto: OrderCreateSchema) -> OrderResponseSchema:
        """
        Creating new order in CRM.
        Args:
            order_dto: DTO with order creation data
        Returns:
            DTO with order data
        """
        pass

    @abstractmethod
    async def create_payment(self, payment_dto: PaymentCreateSchema) -> PaymentResponseSchema:
        """
        Creating new payment in CRM
        Args:
            payment_dto: DTO with payment creation data
        Returns:
            DTO with data of created payment
        Raises:
            Exception: if payment creation failed
        """
        pass
