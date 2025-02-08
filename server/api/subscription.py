from pydantic import BaseModel
class SubscriptionBase(BaseModel):
    source: str
    aggregate: bool
    url: str
    
class SubscriptionInput(SubscriptionBase):
    pass

class SubscriptionOutput(SubscriptionBase):
    id: int | None = None
    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status
from api.user import get_current_user
from api.database import get_database
from storage.model import User, Subscription

router = APIRouter(
    prefix="/subscription",
    tags=["subscription"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", response_model = SubscriptionOutput)
def create(item: SubscriptionInput, current_user: User = Depends(get_current_user)):
    subscription, create = Subscription.get_or_create(
        url = item.url,
        defaults = {
            "source": item.source,
            "aggregate": item.aggregate,
            "auto": False
        }
    )
    if not create:
        if subscription.auto == True:
            subscription.auto == False
            subscription.save()
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Duplicate url",
                headers = {"WWW-Authenticate": "Bearer"},
            )
    return subscription

@router.post("/delete", response_model = SubscriptionOutput)
def delete(item: SubscriptionInput, current_user: User = Depends(get_current_user)):
    subscription = Subscription.get_or_none(Subscription.url == item.url)
    if subscription == None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Subscription not exist",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    subscription.delete_instance()
    return subscription

@router.get("/list", response_model = list[SubscriptionOutput])
def get_list(show_auto: bool = False, offset: int = 0, limit: int | None = None, current_user: User = Depends(get_current_user)):
    subscriptions = Subscription.select().where(Subscription.auto == show_auto).offset(offset)
    if limit != None:
        subscriptions = subscriptions.limit(limit)
    response = []
    for subscription in subscriptions:
        response.append(subscription)
    return response

@router.get("/list/{subscription_source}", response_model = list[SubscriptionOutput])
def get_by_source(subscription_source: str, show_auto: bool = False, offset: int = 0, limit: int | None = None, current_user: User = Depends(get_current_user)):
    subscriptions = Subscription.select().where(Subscription.auto == show_auto).where(Subscription.source == subscription_source).offset(offset)
    if limit != None:
        subscriptions = subscriptions.limit(limit)
    response = []
    for subscription in subscriptions:
        response.append(subscription)
    return response

@router.get("/get/{subscription_id}", response_model = SubscriptionOutput)
def get_subscription(subscription_id: int):
    subscription = Subscription.get_or_none(Subscription.id == subscription_id)
    if not subscription:
        raise HTTPException(status_code = 404, detail = "Subscription not found")
    return subscription

