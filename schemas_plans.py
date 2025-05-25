
from pydantic import BaseModel
from typing import Optional

class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass

class PlanInDB(PlanBase):
    id: int
