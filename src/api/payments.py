from fastapi import APIRouter, HTTPException, Depends
from src.schemas.payments import PaymentCreateSchema, PaymentResponseSchema
from src.services.integrations import BaseCRMService, get_crm_service
from src.core.logger import get_logger

logger = get_logger("api.payments")
router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponseSchema)
async def create_payment(
    payment: PaymentCreateSchema, service: BaseCRMService = Depends(get_crm_service)
) -> PaymentResponseSchema:
    """
    Creating new payment in CRM
    Required fields:
    - order_id: order ID
    - amount: payment amount
    - type: payment type (ENUM: cash, bank_card, e_money, bank_transfer, credit)
    - status: payment status (ENUM: not-paid, invoice, wait-approved, payment-start, canceled, fail, paid, returned)
    Optional fields:
    - paid_at: payment date (format: YYYY-MM-DD)
    - comment: payment comment
    """
    try:
        logger.info(
            "POST /payments/ request received",
            extra={
                "order_id": payment.order_id,
                "amount": payment.amount,
                "payment_type": payment.type,
            },
        )
        result = await service.create_payment(payment)
        logger.info(
            f"POST /payments/ completed successfully, created payment ID: {result.id} " f"for order {payment.order_id}"
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in POST /payments/: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
