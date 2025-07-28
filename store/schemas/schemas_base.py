from datetime import datetime
from decimal import Decimal
from pydantic import UUID4, BaseModel, ConfigDict, Field, model_validator


class BaseSchemaMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OutSchema(BaseModel):
    id: UUID4 = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()

    @model_validator(mode="before")
    def set_schema(cls, data):
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = Decimal(str(value))

        return data
