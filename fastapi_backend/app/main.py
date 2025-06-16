from fastapi import FastAPI
from .celery_app import celery_app
from fastapi.middleware.cors import CORSMiddleware
from kombu.exceptions import OperationalError
from .utils import simple_generate_unique_route_id
from app.routes.block_data import router as block_data_router
from app.routes.exchange_rate import router as exchange_rate_router
from app.routes.mwh_revenue import router as mwh_revenue_router
from app.routes.asic import router as asic_router
from app.config import settings

app = FastAPI(
    generate_unique_id_function=simple_generate_unique_route_id,
    openapi_url=settings.OPENAPI_URL,
)

@app.on_event("startup")
def startup_event():
    try:
        # this is synchronous
        celery_app.connection().ensure_connection(max_retries=3)
        print("✅ Celery broker connected")
    except OperationalError as e:
        print("❌ Could not connect to broker:", e)

# Middleware for CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(block_data_router, prefix="/block_data")
app.include_router(exchange_rate_router, prefix="/exchange_rate")
app.include_router(mwh_revenue_router, prefix="/mwh_revenue")
app.include_router(asic_router, prefix="/asic")