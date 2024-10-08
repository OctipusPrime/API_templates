"""
Main FastAPI application
"""

import datetime
import subprocess
from contextlib import asynccontextmanager
import os
from openai import AzureOpenAI
from fastapi import FastAPI, Query, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import uvicorn
from functions import get_llm_response

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run before the application starts
    # Capture deployment timestamp
    app.deployment_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    # Get Git commit hash so you can check if you are running new version
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except Exception:
        commit_hash = "Unknown"
    app.commit_hash = commit_hash

    # Initialize Azure Key Vault client
    kv_uri =  os.environ["KEY_VAULT_URI"] # this env var was added to the web app in the bicep file
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=credential)
    app.key_vault_client = client

    # Initialize OpenAI client
    # The endpoint and key are stored in Azure Key Vault, you must add them there for the app to work
    oai_endpoint = client.get_secret("openai-endpoint").value
    oai_key = client.get_secret("openai-key").value
    oai_client = AzureOpenAI(api_key=oai_key, azure_endpoint=oai_endpoint, api_version="2024-05-01-preview")
    app.oai_client = oai_client

    yield

app = FastAPI(lifespan=lifespan)

# Baseline route, this is what you see when you go to the root URL
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    app = request.app
    deployment_timestamp = app.deployment_timestamp
    version = "1.0.0"  # Update as needed
    commit_hash = app.commit_hash

    # List of API endpoints
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            for method in route.methods:
                if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    routes.append({"path": route.path, "method": method})

    # Health status checks
    health_status = {}
    try:
        # Check Azure Key Vault connectivity
        app.key_vault_client.list_properties_of_secrets()
        health_status["Azure Key Vault"] = "Healthy"
    except Exception:
        health_status["Azure Key Vault"] = "Unhealthy"

    try:
        # Check OpenAI connectivity
        test_messages = [
            {"role": "system", "content": "Follow user instructions"},
            {"role": "user", "content": "Say 'Healthy'"}
        ]
        test_response = get_llm_response(app.oai_client, test_messages)
        health_status["OpenAI"] = test_response
    except Exception:
        health_status["OpenAI"] = "Unhealthy"

    # Populate a prepared html template with gathered information
    return templates.TemplateResponse("index.html", {
        "request": request,
        "deployment_timestamp": deployment_timestamp,
        "version": version,
        "commit_hash": commit_hash,
        "routes": routes,
        "health_status": health_status
    })

# Route to interact with the OpenAI model, ready for any other code to be added
@app.get("/ask_gpt", response_class=JSONResponse)
async def ask_gpt(
    request: Request,
    prompt: str = Query(..., description="Prompt to send to the OpenAI model"),
    key_name: str = Query(..., description="Name of the key to check in the Key Vault"),
    # Header means the value will be sercret and not visible in the URL
    api_key: str = Header(..., alias="X-API-Key", description="API key to check against the Key Vault")
):
    app = request.app
    try:
        # Check if the key matches the value in the Key Vault
        secret = app.key_vault_client.get_secret(key_name)
        if secret.value == api_key:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            response = get_llm_response(app.oai_client, messages)
            return {"status": "success", "message": response}
        else:
            return {"status": "failure", "message": "Key value does not match"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
