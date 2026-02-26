from fastapi import HTTPException

# API key → tenant + role + allowed models
API_KEYS = {
    "admin_key": {
        "tenant": "admin",
        "role": "admin",
        "models": ["kimi", "opus", "sonnet", "azure"]
    },
    "dev_key": {
        "tenant": "dev_team",
        "role": "dev",
        "models": ["kimi", "sonnet"]
    },
    "analyst_key": {
        "tenant": "analytics",
        "role": "analyst",
        "models": ["sonnet"]
    },
    "infra_key": {
        "tenant": "infra",
        "role": "infra",
        "models": ["azure"]
    }
}


def authorize(api_key: str, model: str):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    info = API_KEYS[api_key]

    if model not in info["models"]:
        raise HTTPException(status_code=403, detail="Access denied for this model")

    return info["tenant"], info["role"]
