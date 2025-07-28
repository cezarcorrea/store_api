from fastapi import FastAPI
from store.core.core_config import settings
from store.routers import api_router
from store.db.db_postgres import db_client


class App(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
            version="0.0.1",
            title=settings.PROJECT_NAME,
            root_path=settings.ROOT_PATH
        )
        self.add_event_handler("startup", self.on_startup)
        self.add_event_handler("shutdown", self.on_shutdown)

    async def on_startup(self) -> None:
        print("Iniciando a aplicação...")
        await db_client.connect(settings.DATABASE_URL)
        print("Conexão com o banco de dados estabelecida.")

    async def on_shutdown(self) -> None:
        print("Desligando a aplicação...")
        await db_client.disconnect()
        print("Conexão com o banco de dados fechada.")


# Mantenha esta linha se você também roda o app com uvicorn store.main:app
app = App()
app.include_router(api_router)


# --- NOVO: Função para obter a instância da aplicação ---
def get_application() -> FastAPI:
    """Retorna uma nova instância do aplicativo FastAPI."""
    _app = App()
    _app.include_router(api_router)
    return _app
