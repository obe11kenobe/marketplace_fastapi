from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from .config import settings
from .database import init_db
from .routes import products_router, categories_router, cart_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url='/api/docs',
    redoc_url='/api/redoc'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

app.include_router(products_router)
app.include_router(categories_router)
app.include_router(cart_router)

@app.on_event('startup')
def on_startup():
    init_db()

@app.get('/health')
def health_check():
    return {'status': 'healthy'}

# ponytail: собранный фронт отдаём этим же приложением — same-origin, CORS в проде не участвует.
# В dev фронт живёт на 5173 и ходит сюда через прокси Vite; там достаточно cors_origins.
class SPAStaticFiles(StaticFiles):
    """Неизвестный путь отдаёт index.html — иначе перезагрузка на /cart вернёт 404."""

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise
            return await super().get_response('index.html', scope)


# Монтируем последним, иначе перекроет /api.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / 'frontend' / 'dist'
if FRONTEND_DIST.is_dir():
    app.mount('/', SPAStaticFiles(directory=FRONTEND_DIST, html=True), name='frontend')