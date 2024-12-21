import asyncio

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import observedValue, sensorType
from app.background.bleScanTask import bleScanTask


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    task = asyncio.create_task(bleScanTask(stop_event))

    yield

    stop_event.set()
    await task


app = FastAPI(lifespan=lifespan)
app.include_router(observedValue.router, prefix="/api/v1", tags=["observed-values"])
app.include_router(sensorType.router, prefix="/api/v1", tags=["sensor-types"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
