from fastapi import HTTPException, Header

# Simple in-memory API key role mapping (enterprise can move to DB later)
API_KEYS = {
    "admin_key": {
        "role": "admin",
        "models": ["kimi", "opus", "sonnet", "azure"]
    },
    "dev_key": {
        "role": "dev",
        "models": ["kimi", "sonnet"]
    },
    "analyst_key": {
        "role": "analyst",
        "models": ["sonnet"]
    },
    "infra_key": {
        "role": "infra",
        "models": ["azure"]
    }
}


def authorize(api_key: str, model: str):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if model not in API_KEYS[api_key]["models"]:
        raise HTTPException(status_code=403, detail="Access denied for this model")

    return API_KEYS[api_key]["role"]
