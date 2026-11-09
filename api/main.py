"""Infrastructure API. Dataset-specific prediction is intentionally pending."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.schemas import HealthResponse, ModelInfo
from classification.settings import get_settings

app = FastAPI(title="Classification API", version="0.1.0")


def unavailable() -> JSONResponse:
    configured = bool(get_settings().model_uri)
    return JSONResponse(
        status_code=503,
        content={
            "code": "MODEL_LOADING_NOT_IMPLEMENTED" if configured else "MODEL_NOT_CONFIGURED",
            "message": "Model loading and prediction will be implemented after dataset selection."
            if configured
            else "No trained model is configured yet.",
        },
    )


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")


@app.get("/ready", responses={503: {"description": "No model is loaded"}})
def ready():
    return unavailable()


@app.get("/model-info", response_model=ModelInfo)
def model_info():
    return ModelInfo(
        configured=bool(get_settings().model_uri),
        loaded=False,
        message="Dataset selection, training, and model loading are pending.",
    )


@app.post("/predict", responses={503: {"description": "Prediction is not available yet"}})
def predict():
    return unavailable()
