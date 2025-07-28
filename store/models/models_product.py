from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import Field


# Esta classe representa a estrutura de dados de um produto
class ProductModel:
    """
    Representa um modelo de dados para um produto.
    """

    id: UUID = Field(..., description="Unique identifier of the product")
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., description="Product quantity")
    price: Decimal = Field(..., description="Product price")
    status: bool = Field(
        ..., description="Product status (e.g., available, out of stock)"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the product was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the product was last updated"
    )

    def __init__(self, **data):
        """
        Inicializa o modelo do produto com os dados fornecidos.
        """
        for key, value in data.items():
            setattr(self, key, value)

    def to_dict(self):
        """
        Converte o modelo do produto para um dicionário.
        Útil para serialização ou depuração.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "quantity": self.quantity,
            "price": str(self.price),  # Converte Decimal para string para serialização
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Cria uma instância do modelo do produto a partir de um dicionário.
        Útil para desserialização de dados do banco de dados, por exemplo.
        """
        # Garante que 'id' é um UUID
        if "id" in data and isinstance(data["id"], str):
            data["id"] = UUID(data["id"])

        # Garante que 'price' é um Decimal
        if "price" in data and not isinstance(data["price"], Decimal):
            data["price"] = Decimal(str(data["price"]))

        # Garante que os campos de data/hora sejam datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        return cls(**data)
