from pydantic import BaseModel, Field
from enum import Enum
from src.schemas.customers import CustomerGetSchema, CustomerResponseWithIdOnlySchema


class OrderTypeEnum(str, Enum):
    """By default available only main order type."""

    main = "main"
    # web = "web"
    # store = "store"
    # call = "call"


class OrderMethodEnum(str, Enum):
    """By default available only order type."""

    phone = "phone"
    shopping_cart = "shopping-cart"
    one_click = "one-click"
    price_decrease_request = "price-decrease-request"
    landing_page = "landing-page"
    offline = "offline"
    app = "app"
    live_chat = "live-chat"
    terminal = "terminal"
    missed_call = "missed-call"
    messenger = "messenger"


class OfferSchema(BaseModel):
    name: str
    id: int


class OrderItemSchema(BaseModel):
    quantity: float
    initial_price: float = Field(alias="initialPrice")
    purchase_price: float = Field(alias="purchasePrice")
    product_name: str = Field(alias="productName")
    model_config = {"populate_by_name": True}


class OrderItemGetSchema(OrderItemSchema):
    id: int
    quantity: float
    initial_price: float = Field(alias="initialPrice")
    purchase_price: float = Field(alias="purchasePrice")
    offer: OfferSchema
    model_config = {"populate_by_name": True}


class OrderCreateSchema(BaseModel):
    customer: CustomerResponseWithIdOnlySchema
    items: list[OrderItemSchema]
    number: str
    order_type: OrderTypeEnum = Field(default=OrderTypeEnum.main, alias="orderType")
    order_method: OrderMethodEnum = Field(default=OrderMethodEnum.phone, alias="orderMethod")
    model_config = {"populate_by_name": True}


class OrderResponseSchema(BaseModel):
    id: int
    number: str
    customer: CustomerGetSchema
    items: list[OrderItemGetSchema]
    total_amount: float = Field(alias="totalSumm")
    created_at: str = Field(alias="createdAt")
    model_config = {"populate_by_name": True}


class OrdersListResponse(BaseModel):
    """Модель ответа для списка заказов"""

    orders: list[OrderResponseSchema]
    pagination: dict | None = None
