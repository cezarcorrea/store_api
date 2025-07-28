from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from store.core.core_exceptions import NotFoundException

from store.schemas.schemas_product import (
    ProductIn,
    ProductOut,
    ProductUpdate,
    ProductUpdateOut,
)
from store.usecases.usecases_product import ProductUsecase
from store.dependencies import get_db_pool
from psycopg_pool import AsyncConnectionPool

router = APIRouter(tags=["products"])


# Nova função de dependência para criar o ProductUsecase
# Ela recebe o pool e cria o usecase.
def get_product_usecase(
    pool: AsyncConnectionPool = Depends(get_db_pool),
) -> ProductUsecase:
    return ProductUsecase(pool=pool)


# insere novo produto no Banco
@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def inserir_novo_produto(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends(get_product_usecase)
) -> ProductOut:
    return await usecase.create(body=body)


# Pesquisa produto no Banco por ID
@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def pesquisar_por_ID(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends(get_product_usecase)
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def pesquisar_produto(
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> List[ProductOut]:
    return await usecase.query()


# Edita produto no Banco por ID
@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def editar_por_ID(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> ProductUpdateOut:
    return await usecase.update(id=id, body=body)


# Deleta produto no Banco
@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_por_ID(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends(get_product_usecase)
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
