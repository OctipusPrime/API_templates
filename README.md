# API template with Azure IaC
Deploy a simple API on Azure. 

## Set-up

### Deploy the infrastructure

First you have to set up you new resource group. 

```bash
az login
```
To login into the cloud, then make sure that you are in the right subscription
```bash
az account show
```
This tells you in which you are. If it's the wrong one run
```bash
az account list
```
List all subscriptions that are available to you and copy the `id`. Then use it to switch to that subscription with
```bash
az account set --subscription "xxxxx-xxxxx-xxxxx"
```

Now that you are in the correct subscription, you can create a new resource group. 
```bash
az group create --name "string" --location "string"
```
Set this resource group as a default for future commands
```bash
 az configure --defaults group="resource_group_name"
```

Now you can use the `resources.bicep` to deploy the infrastructure. They will be deployed in the same location as is the resource group by default. 
```bash
az deployment group create --template-file resources.bicep
```
The name of the deployment allows you to differentiate different deployments, without it it's named after the bicep file name. 
This should deploy
- web app plan
- web app
- key vault
- add keyvault uri to the web app as env variable
See more in `resource.bicep`


> [!warning] Azure OpenAI is NOT included
> I haven't found a way to deploy the Azure OpenAI via bicep. You either need to deploy it manually via the Azure Portal or use an existing one. 

### Get access rights

In order to test the app locally, you must get access rights to the Key Vault. Open the created Azure Key Vault (found in the resource group you set up for it), go to "Access policies", "Create", Select at least "Secret permissions - get, list", Add yourself, skip application (it was added in the bicep file) and create. 

> [!NOTE] Permission issues
> If you do not have rights to give the permissions to yourself, request the assignment on \#ds-it-helpdesk. Include the subscription, resource group and keyvault name in the request. Best to get the "Key Vault Administrator" role for the keyvault. 

### Add secrets

Now you need to add secrets for the OpenAI endpoint and api-key. 

Go to the Azure OpenAI resource you will be using (it was NOT deployed into the resource group), get the endpoint and secret, and save the as **Secrets** in the Key Vault under `openai-endpoint` and `openai-key`. 
(Go to the Key Vault in the browser, under "Objects" find secrets and add secret)

Add another secret by default called `Test` which will be serving as a gateway key for anyone requesting data from. This one is just for testing purposes, you can add any number of secrets under different names, requests need to contain the name and the secret value, if both match, they get through. 

Add the `Test` secret to variables in your terminal by
```bash
export Test=<secret_value>
```

### Test the app locally

For local testing turn the app locally via:
```bash
export KEY_VAULT_URI=$(az deployment group show --resource-group API_deployment_test --name resources --query properties.outputs.keyVaultUri.value -o tsv) && uvicorn main:app --reload
```
This will get the Key Vault URL environment variable and allows you to turn the app on. 

Now you can test whether your access to the Key Vault and GPT works by navigating to the `localhost:8000` website in your browser. If under "Service Health Status" are both services marked as Healthy, you are good to go. Otherwise, check your access to the Key Vault and openai endpoints respectively. 

You can also run 
```bash
python3 test_API_access.py local
```
to check whether the baseline API works and returns a json. 

### Deploy the app to the Web App Service

Now you need to deploy the app code to the running web app. Easiest way is to get the Azure extension in VS Code and deploy it via the `Azure App Service: Deploy to Web App` command. Make sure to find the Web App that was deployed via the bicep file above. It's name should be something like `webapp-xxxxxxxxxx` with `x` being letters or numbers. 

Now for testing whether the API works first export the name of the url (can be found on Azure Portal under the WebApp.)
Eg: `export URL=https://webapp-ta2lkvguyvay6.azurewebsites.net`

You can then test access by 
```bash
python3 test_API_access.py cloud
```

## FAQ

### How does limiting access work?
In the request, the user specifies a `key_name` and `api_key`. The code goes to the Azure Key Vault and checks whether there is a value for `key_name` and if it matches value in `api_key`. If so, it allows access and runs the rest of the code, otherwise it throws "SecretNotFound" (if the `key_name` is not in the Key Vault) or "Key value does not match" error if the `api_key` does not match. 


### Are the API keys generated automatically?
No. You have to add OpenAI endpoint and api key manually. You also need to add a secret that limits access to the API. If you feel like adding this functionality, it will be appreciated. 