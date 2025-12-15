from fastapi import APIRouter, Path, HTTPException, Depends, Query
from src.schemas.customers import CustomerGetOrdersSchema
from src.schemas.orders import (
    OrderCreateSchema,
    OrderResponseSchema,
    OrdersListResponse,
)
from src.services.integrations import BaseCRMService, get_crm_service
from src.core.logger import get_logger

logger = get_logger("api.orders")
router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/customer/{customer_id}", response_model=OrdersListResponse)
async def get_customer_orders(
    customer_id: int = Path(..., description="customer ID"),
    limit: int = Query(20, ge=1, le=100, description="orders per page"),
    page: int = Query(1, ge=1, description="page number"),
    service: BaseCRMService = Depends(get_crm_service),
) -> OrdersListResponse:
    """
    Get list of orders for customer
    Returns all orders associated with the specified customer.
    """
    try:
        logger.info(
            f"GET /orders/customer/{customer_id} request received",
            extra={
                "customer_id": customer_id,
                "pagination": {"limit": limit, "page": page},
            },
        )
        data = {"customer_id": customer_id, "limit": limit, "page": page}
        customer_data = CustomerGetOrdersSchema(**data)
        result = await service.get_customer_orders(customer_data=customer_data)
        orders_count = len(result.orders)
        logger.info(f"GET /orders/customer/{customer_id} completed successfully, " f"returned {orders_count} orders")
        return result
    except HTTPException:
        logger.error(f"HTTPException in GET /orders/customer/{customer_id}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in GET /orders/customer/{customer_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=OrderResponseSchema)
async def create_order(
    order: OrderCreateSchema, service: BaseCRMService = Depends(get_crm_service)
) -> OrderResponseSchema:
    """
    Creating new order in CRM.
    Required fields:
    - number: order number
    - order_type: order type (ENUM: main)
    - order_method: order method (ENUM: phone, shopping-cart, one-click, price-decrease-request,
        landing-page, offline, app, live-chat, terminal, missed-call, messenger)
    - customer.id: customer ID
    - items: list of items
        item fields:
            - quantity: amount of product
            - initial_price: initial price of product
            - purchase_price: purchase price of product
            - product_name: product name

    """
    try:
        order_number = order.number
        customer_id = order.customer.id
        items_count = len(order.items)
        logger.info(
            "POST /orders/ request received",
            extra={
                "order_number": order_number,
                "customer_id": customer_id,
                "items_count": items_count,
            },
        )
        result = await service.create_order(order)
        logger.info(f"POST /orders/ completed successfully, created order ID: {result.id}, " f"number: {order_number}")
        return result
    except HTTPException:
        logger.error("HTTPException in POST /orders/:", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in POST /orders/: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
