from decimal import Decimal

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_controller_create_should_return_success(api_client, product_data):
    import copy

    data = copy.deepcopy(product_data)
    data["price"] = float(data["price"])

    response = await api_client.post("/products/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    content = response.json()

    # Valida só os campos importantes
    assert content["name"] == product_data["name"]
    assert content["quantity"] == product_data["quantity"]
    assert float(content["price"]) == float(product_data["price"])
    assert content["status"] is True


@pytest.mark.asyncio
async def test_controller_get_should_return_success(
    api_client, products_url, product_inserted
):
    response = await api_client.get(f"{products_url}{product_inserted.id}")

    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK

    assert content["id"] == str(product_inserted.id)
    assert content["name"] == "Iphone 14 Pro Max"
    assert content["quantity"] == 10
    assert float(content["price"]) == float(product_inserted.price)
    assert content["status"] is True


@pytest.mark.asyncio
async def test_controller_get_should_return_not_found(api_client, products_url):
    response = await api_client.get(
        f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }


@pytest.mark.asyncio
async def test_controller_query_should_return_success(
    api_client, products_url, products_inserted
):
    response = await api_client.get(products_url)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_controller_patch_should_return_success(
    api_client, products_url, product_inserted
):
    response = await api_client.patch(
        f"{products_url}{product_inserted.id}", json={"price": "7.50"}
    )

    content = response.json()
    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK

    # Compara com precisão
    assert Decimal(content["price"]) == Decimal("7.50")
    assert content["id"] == str(product_inserted.id)
    assert content["name"] == product_inserted.name
    assert content["quantity"] == product_inserted.quantity
    assert content["status"] == product_inserted.status


@pytest.mark.asyncio
async def test_controller_delete_should_return_no_content(
    api_client, products_url, product_inserted
):
    response = await api_client.delete(f"{products_url}{product_inserted.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_controller_delete_should_return_not_found(api_client, products_url):
    response = await api_client.delete(
        f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }
