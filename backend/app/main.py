from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from authx.exceptions import (
    JWTDecodeError,
    RevokedTokenError,
    TokenExpiredError,
    TokenInvalidSignatureError,
)
from .config import settings
from .products import products_router
from .categories import categories_router
from .cart import cart_router
from .auth import auth_router
from .auth.security.security import security
from .orders import orders_router
from .wishlist import wishlist_router
from .reviews import reviews_router

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
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(wishlist_router)
app.include_router(reviews_router)

security.handle_errors(app)

def _unauthorized(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Недействительный токен"})

for _exc in (JWTDecodeError, TokenExpiredError, TokenInvalidSignatureError, RevokedTokenError):
    app.add_exception_handler(_exc, _unauthorized)

@app.get('/health')
def health_check():
    return {'status': 'healthy'}

class SPAStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise
            return await super().get_response('index.html', scope)

FRONTEND_DIST = Path(__file__).resolve().parents[2] / 'frontend' / 'dist'
if FRONTEND_DIST.is_dir():
    app.mount('/', SPAStaticFiles(directory=FRONTEND_DIST, html=True), name='frontend')
