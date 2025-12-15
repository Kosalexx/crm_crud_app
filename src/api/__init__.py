from .customers import router as customers_router
from .orders import router as orders_router
from .payments import router as payments_router


__all__ = ["customers_router", "orders_router", "payments_router"]
