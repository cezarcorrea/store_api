from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID
from pydantic import AfterValidator, Field
from store.schemas.schemas_base import BaseSchemaMixin, OutSchema


class ProductBase(BaseSchemaMixin):
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., description="Product quantity")
    price: Decimal = Field(..., description="Product price")
    status: bool = Field(..., description="Product status")


class ProductIn(ProductBase, BaseSchemaMixin):
    name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., description="Quantidade em estoque")
    price: Decimal = Field(..., description="Preço do produto")
    status: bool = Field(..., description="Status do produto (ativo/inativo)")
    description: Optional[str] = Field(
        None, description="Descrição detalhada do produto"
    )


class ProductOut(ProductIn, OutSchema):
    id: UUID = Field(..., description="ID do produto")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")


def convert_decimal(v):
    return Decimal(str(v))


Decimal_ = Annotated[Decimal, AfterValidator(convert_decimal)]


class ProductUpdate(BaseSchemaMixin):
    quantity: Optional[int] = Field(None, description="Product quantity")
    price: Optional[Decimal_] = Field(None, description="Product price")
    status: Optional[bool] = Field(None, description="Product status")


class ProductUpdateOut(ProductOut):
    ...
