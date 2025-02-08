from pydantic import BaseModel

class ProviderUpdate(BaseModel):
    id: int
    mikan_id: int | None = None
    name: str | None = None
    alternative_name: str | None = None

class ProviderOutput(BaseModel):
    id: int
    mikan_id: int | None = None
    name: str
    alternative_name: str


from fastapi import APIRouter, Depends, HTTPException, status

from storage.model import User, Provider
from api.database import get_database
from api.user import get_current_user

router = APIRouter(
    prefix="/provider",
    tags=["provider"],
    dependencies=[Depends(get_database)],
    responses={404: {"description": "Not found"}},
)

@router.get("/{index}", response_model = ProviderOutput)
def get_provider(index: int, current_user: User = Depends(get_current_user)):
    provider = Provider.get_or_none(Provider.id == index)
    if provider == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Provider not found."
        )
    return provider

@router.post("/update", response_model = ProviderOutput)
def update_provider(item: ProviderUpdate, current_user: User = Depends(get_current_user)):
    provider = Provider.get_or_none(Provider.id == item.id)
    if provider == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Provider not found."
        )
    for field_name, field in item.model_fields.items():
        if getattr(item, field_name) != None and hasattr(provider, field_name):
            setattr(provider, field_name, getattr(item, field_name))
    provider.save()
    return provider