from fastapi import APIRouter, Depends
from src.model.api.order_request import CreateOrderRequest
from src.model.view.order_view import OrderCreatedView
from src.service.order_service import OrderService
from src.config.dependency import get_order_service

router = APIRouter(prefix="/v1/order", tags=["orders"])


@router.post("", response_model=OrderCreatedView, status_code=202)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service)
):
    """
    Create a new restaurant order.
    Creates order record and enqueues meal preparation jobs.
    """
    return service.create_order(request)
