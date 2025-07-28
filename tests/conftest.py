import os
import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator, Any, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from store.main import get_application
from store.schemas.schemas_product import ProductIn, ProductOut, ProductUpdate
from store.usecases.usecases_product import ProductUsecase
from store.db.db_postgres import db_client as global_db_client

# Configuração para Windows, se necessário
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Carrega as variáveis de ambiente (se ainda não carregou via pytest-dotenv)
load_dotenv()


# --- Fixtures de Infraestrutura ---


@pytest.mark.asyncio(scope="session")
def event_loop():
    """Cria um loop de eventos para as fixtures de teste."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database_connection_and_schema():
    """
    Fixture para conectar ao banco de dados usando o global_db_client,
    criar a tabela 'products' (se não existir) e depois desconectar ao
    final da sessão de testes.
    Este fixture garante que o db_client.pool esteja conectado antes de
    qualquer uso.
    """
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        pytest.fail(
            "DATABASE_URL environment variable not set. Please set it to run tests."
        )

    # Conecta o pool de conexões do global_db_client
    print("\n[SETUP] Conectando ao banco de dados e abrindo pool...")
    await global_db_client.connect(dsn)
    print("[SETUP] Conectado ao banco de dados e pool aberto.")

    try:
        # Cria a tabela 'products' se ela não existir
        async with global_db_client.pool.connection() as conn:
            async with conn.cursor() as cur:
                print("[SETUP] Verificando/Criando tabela 'products'...")
                await cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id UUID PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description VARCHAR(1000),
                        quantity INTEGER NOT NULL,
                        price NUMERIC(10, 2) NOT NULL,
                        status BOOLEAN NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """
                )
                await conn.commit()
                print("[SETUP] Tabela 'products' verificada/criada com sucesso.")

        yield

    finally:
        # Desconecta o pool de conexões após todos os testes da sessão
        print("[TEARDOWN] Desconectando do banco de dados e fechando pool...")
        await global_db_client.disconnect()
        print("[TEARDOWN] Banco de dados desconectado e pool fechado.")


@pytest_asyncio.fixture(autouse=True)
async def clear_products_table(setup_database_connection_and_schema):
    """
    Limpa a tabela 'products' antes de cada teste para garantir isolamento.
    Depende de setup_database_connection_and_schema para garantir que o pool
    esteja conectado.
    """
    print(
        f"[PRE-TEST] Limpando tabela 'products' antes de cada teste: "
        f"{datetime.now().isoformat()}"
    )
    # Use global_db_client.pool para obter a conexão
    async with global_db_client.pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("TRUNCATE TABLE products RESTART IDENTITY CASCADE;")
            await conn.commit()
    print("[PRE-TEST] Tabela 'products' limpa.")


@pytest_asyncio.fixture(scope="function")
async def api_client(
    setup_database_connection_and_schema,
) -> AsyncGenerator[AsyncClient, Any]:
    app = get_application()
    """
    Retorna um cliente HTTP assíncrono para testar a aplicação FastAPI.
    Garante que o DB esteja configurado antes de iniciar o cliente.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# --- Fixture para o Usecase (INJEÇÃO DE DEPENDÊNCIA) ---


@pytest_asyncio.fixture
async def product_usecase(
    setup_database_connection_and_schema,
) -> ProductUsecase:
    """
    Fornece uma instância de ProductUsecase para os testes.
    Esta instância é criada COM O POOL DE CONEXÃO CORRETO.
    """
    if global_db_client.pool is None or global_db_client.pool.closed:
        pytest.fail(
            "O pool de banco de dados não foi inicializado ou está fechado. "
            "Verifique o ambiente setup_database_connection_and_schema fixture."
        )

    # Passa o pool de conexão para o construtor do ProductUsecase
    return ProductUsecase(pool=global_db_client.pool)


# --- Fixtures para Dados de Teste ---


@pytest_asyncio.fixture
def product_id() -> UUID:
    """Retorna um UUID fixo para testes de produto único."""
    return UUID("f596b669-e77a-4c1c-9029-231a59052b61")


@pytest_asyncio.fixture
def product_data() -> dict:
    """Dados básicos de um produto para criação."""
    return {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": Decimal("8500.00"),
        "status": True,
        "description": "Apple.",
    }


@pytest_asyncio.fixture
def product_in(product_data: dict) -> ProductIn:
    """Retorna um ProductIn válido."""
    return ProductIn(**product_data)


@pytest_asyncio.fixture
async def product_inserted(
    product_usecase: ProductUsecase, product_in: ProductIn
) -> ProductOut:
    """
    Insere um produto no banco de dados e retorna o ProductOut.
    Agora usa a instância de product_usecase injetada pela fixture.
    """
    return await product_usecase.create(body=product_in)


@pytest_asyncio.fixture
async def products_inserted(
    product_usecase: ProductUsecase, product_in: ProductIn
) -> List[ProductOut]:
    """
    Insere múltiplos produtos no banco de dados e retorna uma lista de ProductOut.
    Agora usa a instância de product_usecase injetada pela fixture.
    """
    products = []
    for i in range(3):
        modified_product_in = product_in.model_copy(update={"name": f"Product {i+1}"})
        products.append(await product_usecase.create(body=modified_product_in))
    return products


@pytest_asyncio.fixture
def product_up() -> ProductUpdate:
    """Retorna um ProductUpdate para testes de atualização."""
    return ProductUpdate(price=Decimal("7500.00"), quantity=5)


@pytest_asyncio.fixture
def products_url() -> str:
    """Retorna a URL base para a API de produtos."""
    return "/products/"
