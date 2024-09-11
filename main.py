from fastapi import FastAPI, Query, Header
from fastapi.responses import JSONResponse
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import uvicorn

app = FastAPI()

# Initialize Azure Key Vault client
key_vault_name = "keyvault-123456132465A"
kv_uri = f"https://{key_vault_name}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)

@app.get("/check-key", response_class=JSONResponse)
async def check_key(
    key_name: str = Query(..., description="Name of the key to check in the Key Vault"),
    api_key: str = Header(..., alias="X-API-Key", description="API key to check against the Key Vault")
):
    try:
        # Fetch the secret from Azure Key Vault
        secret = client.get_secret(key_name)
        if secret.value == api_key:
            return {"status": "success", "message": "Key value matches"}
        else:
            return {"status": "failure", "message": "Key value does not match"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)