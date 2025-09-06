from bson import ObjectId
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic_core import core_schema
from typing import Any
from datetime import datetime
from typing import Optional
from app.models.BaseModel.common import Question

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v), return_schema=core_schema.str_schema()
            )
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> dict:
        return {"type": "string"}


class Score(BaseModel):
    createdAt: str | None = None
    score: int
    question_answer: list[str] | None = None


class Response(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: Optional[PyObjectId] = Field(default=None)
    url_id: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    questions: list[Question] | None = None
    quiz_type: str
    difficulty: str
    numbers: int | None = None
    score: list[Score] | None = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        extra = "forbid"
        arbitrary_types_allowed = True


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str
    password: str | None = None
    responses: list[PyObjectId] | None = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        extra = "forbid"
        arbitrary_types_allowed = True

class UserResponse(BaseModel):
    user_id: PyObjectId
    