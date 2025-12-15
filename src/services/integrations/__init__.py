from src.services.integrations.base_crm import BaseCRMService
from src.services.integrations.retail_crm import RetailCRMService
from typing import AsyncGenerator


async def get_crm_service() -> AsyncGenerator[BaseCRMService, None]:
    """
    Context manager for getting CRM service.
    Automatically closes connection with CRM system.
    Used in FastAPI dependencies.

    Yields:
        Instance of CRM service (by default RetailCRMService)
    """
    service = RetailCRMService()
    try:
        yield service
    finally:
        await service.close()


__all__ = [
    "BaseCRMService",
    "RetailCRMService",
    "get_crm_service",
]
