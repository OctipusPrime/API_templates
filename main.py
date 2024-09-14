from openai import AzureOpenAI
from fastapi import FastAPI, Query, Header
from fastapi.responses import JSONResponse
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import uvicorn
from functions import get_llm_response


app = FastAPI()

# Initialize Azure Key Vault client
key_vault_name = "keyvault-123456132465A"
kv_uri = f"https://{key_vault_name}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)

# Initialize OpenAI client
oai_endpoint = client.get_secret("openai-endpoint").value
oai_key = client.get_secret("openai-key").value
oai_client = AzureOpenAI(api_key=oai_key, azure_endpoint=oai_endpoint,api_version="2024-05-01-preview")



@app.get("/check-key", response_class=JSONResponse)
async def check_key(
    prompt: str = Query(..., description="Prompt to send to the OpenAI model"),
    key_name: str = Query(..., description="Name of the key to check in the Key Vault"),
    api_key: str = Header(..., alias="X-API-Key", description="API key to check against the Key Vault")
):
    try:
        # Fetch the secret from Azure Key Vault
        secret = client.get_secret(key_name)
        if secret.value == api_key:
            messages = [{"role": "system", "content": "You are a helpful assistant."}, 
                        {"role": "user", "content": prompt}]
            response = get_llm_response(oai_client, messages)
            return {"status": "success", "message": response}
        else:
            return {"status": "failure", "message": "Key value does not match"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)