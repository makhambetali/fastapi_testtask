from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
import time



class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Message(BaseModel):
    content: str
    from_user_id: int
    to_user_id: int
    publish_timestamp: Optional[float] = Field(default_factory=time.time)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
