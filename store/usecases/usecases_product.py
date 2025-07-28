from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from store.models.models_product import ProductModel
from store.schemas.schemas_product import (
    ProductIn,
    ProductOut,
    ProductUpdate,
    ProductUpdateOut,
)
from store.core.core_exceptions import NotFoundException
from psycopg_pool import AsyncConnectionPool


class ProductUsecase:
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool

    async def create(self, body: ProductIn) -> ProductOut:
        product_id = uuid4()  # Gerar UUID para o ID do produto
        created_at = datetime.now()  # Timestamp de criação
        updated_at = created_at  # Inicialmente o mesmo

        # Crie um ProductModel com os dados de entrada e os IDs/timestamps
        product_model = ProductModel(
            id=product_id,
            created_at=created_at,
            updated_at=updated_at,
            **body.model_dump(),  # inclui nome, preco, quantidade, status, etc.
        )

        async with self.pool.connection() as conn:  # Obtém uma conexão do pool
            async with conn.cursor() as cur:  # Obtém um cursor para executar SQL
                # Comando SQL para inserção
                sql = """
                INSERT INTO products (id, name, description, price, quantity,
                status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, name, description, price, quantity, status,
                created_at, updated_at;
                """
                # Executa o comando SQL.
                await cur.execute(
                    sql,
                    (
                        str(product_model.id),
                        product_model.name,
                        product_model.description,
                        product_model.price,
                        product_model.quantity,
                        product_model.status,
                        product_model.created_at,
                        product_model.updated_at,
                    ),
                )

                result = await cur.fetchone()

                if result:
                    return ProductOut(
                        id=result[0],
                        name=result[1],
                        description=result[2],
                        price=result[3],
                        quantity=result[4],
                        status=result[5],
                        created_at=result[6],
                        updated_at=result[7],
                    )
                else:
                    raise Exception("Failed to create product.")

    async def get(self, id: UUID) -> ProductOut:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                sql = (
                    "SELECT id, name, description, price, quantity, status, "
                    "created_at, updated_at FROM products WHERE id = %s;"
                )
                await cur.execute(sql, (str(id),))
                result = await cur.fetchone()

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        # Mapeie os resultados da tupla para ProductOut
        return ProductOut(
            id=result[0],
            name=result[1],
            description=result[2],
            price=result[3],
            quantity=result[4],
            status=result[5],
            created_at=result[6],
            updated_at=result[7],
        )

    async def query(self) -> List[ProductOut]:
        products_list: List[ProductOut] = []
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                sql = (
                    "SELECT id, name, description, price, quantity, status, "
                    "created_at, updated_at FROM products;"
                )
                await cur.execute(sql)
                async for row in cur:
                    products_list.append(
                        ProductOut(
                            id=row[0],
                            name=row[1],
                            description=row[2],
                            price=row[3],
                            quantity=row[4],
                            status=row[5],
                            created_at=row[6],
                            updated_at=row[7],
                        )
                    )
        return products_list

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        # Construi a query de update dinamicamente com base nos campos presentes no body
        update_fields = []
        update_values = []
        counter = 1
        for field, value in body.model_dump(exclude_unset=True).items():
            if field == "id":  # Não atualiza o ID
                continue
            update_fields.append(f"{field} = %s")
            update_values.append(value)
            counter += 1

        # Adiciona updated_at automaticamente
        update_fields.append("updated_at = %s")
        update_values.append(datetime.utcnow())

        if not update_fields:
            return await self.get(id)

        sql = (
            f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s "
            "RETURNING id, name, description, price, quantity, status, "
            "created_at, updated_at;"
        )
        update_values.append(str(id))  # Adicionar o ID para a cláusula WHERE

        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, tuple(update_values))
                result = await cur.fetchone()

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductUpdateOut(
            id=result[0],
            name=result[1],
            description=result[2],
            price=result[3],
            quantity=result[4],
            status=result[5],
            created_at=result[6],
            updated_at=result[7],
        )

    async def delete(self, id: UUID) -> bool:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                sql = "DELETE FROM products WHERE id = %s;"
                await cur.execute(sql, (str(id),))
                deleted_count = cur.rowcount

        if deleted_count == 0:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return True
