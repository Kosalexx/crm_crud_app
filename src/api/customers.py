from fastapi import APIRouter, Query, HTTPException, Depends
from src.schemas.customers import (
    CustomerAddSchema,
    CustomerFiltersSchema,
    CustomerResponseWithIdOnlySchema,
    CustomersListResponseSchema,
)
from src.services.integrations import BaseCRMService
from src.services.integrations import get_crm_service
from src.core.logger import get_logger

logger = get_logger("api.customers")
router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=CustomersListResponseSchema)
async def get_customers(
    name: str | None = Query(None, description="Name filter"),
    email: str | None = Query(None, description="Email filter"),
    created_at_from: str | None = Query(None, description="Registration date from (format: YYYY-MM-DD)"),
    created_at_to: str | None = Query(None, description="Registration date to (format: YYYY-MM-DD)"),
    limit: int = Query(20, ge=1, le=100, description="Amount of customers per page"),
    page: int = Query(1, ge=1, description="page number"),
    service: BaseCRMService = Depends(get_crm_service),
):
    """
    Get list of customers with optional filters.
    Available filters:
    - name: customer name
    - email: customer  email
    - created_at_from: registration date from
    - created_at_to: registration date to
    """
    try:
        filter_dto = CustomerFiltersSchema(
            name=name,
            email=email,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            limit=limit,
            page=page,
        )
        logger.info(
            "GET /customers/ request received",
            extra={
                "filters": {
                    "name": name,
                    "email": email,
                    "created_at_from": created_at_from,
                    "created_at_to": created_at_to,
                },
                "pagination": {"limit": limit, "page": page},
            },
        )
        result = await service.get_customers(filter_dto)
        logger.info("GET /customers/ completed successfully.")
        return result
    except HTTPException:
        logger.error("HTTPException in GET /customers/: HTTPException raised", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in GET /customers/: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=CustomerResponseWithIdOnlySchema)
async def create_customer(
    customer: CustomerAddSchema, service: BaseCRMService = Depends(get_crm_service)
) -> CustomerResponseWithIdOnlySchema:
    """
    Creating new customer in CRM.

    Required fields:
    - first_name: customer first name

    Optional fields:
    - last_name: surname
    - email: email address
    - phones: list of phones
    - birthday: birthday (format: YYYY-MM-DD)
    """
    try:
        logger.info(
            "POST /customers/ request received",
            extra={"first_name": customer.first_name, "email": customer.email},
        )
        result = await service.create_customer(customer)
        customer_id = result.id
        logger.info(f"POST /customers/ completed successfully, created customer ID: {customer_id}")
        return result
    except HTTPException:
        logger.error("HTTPException in POST /customers/: HTTPException raised", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error in POST /customers/: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
