from fastapi import FastAPI, Depends
from workout_api.routers import api_router

app = FastAPI(title="WorkoutApi")
app.include_router(api_router)


"""
# Configura o middleware CORS para permitir solicitações de qualquer origem (*)
app.add_middleware(
    CORSMiddleware,
    # Você também pode especificar origens específicas em vez de "*",
    # por exemplo: ["http://localhost", "https://example.com"]
    allow_origins=["0.0.0.0", "127.0.0.1:3000", "192.168.0.20", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(router)
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level='info')
