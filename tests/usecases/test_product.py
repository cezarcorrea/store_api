import pytest
from uuid import UUID, uuid4
from datetime import datetime

from store.schemas.schemas_product import ProductOut
from store.core.core_exceptions import NotFoundException


@pytest.mark.asyncio
async def test_create_product_success(product_usecase, product_in):
    product = await product_usecase.create(body=product_in)

    assert isinstance(product, ProductOut)
    assert product.name == product_in.name
    assert product.price == product_in.price
    assert isinstance(product.id, UUID)
    assert isinstance(product.created_at, datetime)
    assert isinstance(product.updated_at, datetime)
    assert product.created_at == product.updated_at


@pytest.mark.asyncio
async def test_get_product_success(product_usecase, product_inserted):
    product = await product_usecase.get(id=product_inserted.id)

    assert product.id == product_inserted.id
    assert product.name == product_inserted.name
    assert product.price == product_inserted.price
    assert product.quantity == product_inserted.quantity
    assert product.status == product_inserted.status
    assert product.created_at == product_inserted.created_at
    assert product.updated_at == product_inserted.updated_at


@pytest.mark.asyncio
async def test_get_product_not_found(product_usecase):
    with pytest.raises(NotFoundException) as err:
        await product_usecase.get(id=uuid4())

    assert "Product not found" in str(err.value)


@pytest.mark.asyncio
async def test_query_products_success(product_usecase, products_inserted):
    products = await product_usecase.query()

    assert isinstance(products, list)
    assert len(products) == len(products_inserted)


@pytest.mark.asyncio
async def test_update_product_success(product_usecase, product_inserted, product_up):
    updated_product = await product_usecase.update(
        id=product_inserted.id, body=product_up
    )

    assert updated_product.id == product_inserted.id
    assert updated_product.price == product_up.price
    assert updated_product.quantity == product_up.quantity
    assert updated_product.updated_at > product_inserted.updated_at


@pytest.mark.asyncio
async def test_update_product_not_found(product_usecase, product_up):
    with pytest.raises(NotFoundException) as err:
        await product_usecase.update(id=uuid4(), body=product_up)

    assert "Product not found" in str(err.value)


@pytest.mark.asyncio
async def test_delete_product_success(product_usecase, product_inserted):
    result = await product_usecase.delete(id=product_inserted.id)
    assert result is True

    with pytest.raises(NotFoundException):
        await product_usecase.get(id=product_inserted.id)


@pytest.mark.asyncio
async def test_delete_product_not_found(product_usecase):
    with pytest.raises(NotFoundException) as err:
        await product_usecase.delete(id=uuid4())

    assert "Product not found" in str(err.value)
