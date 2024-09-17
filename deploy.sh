#!/bin/bash

# Variables
RESOURCE_GROUP="YourResourceGroupName"
LOCATION="YourLocation"
DEPLOYMENT_NAME="resourcesDeployment"

# Login to Azure
az login

# Set Default Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION
az configure --defaults group=$RESOURCE_GROUP

# Deploy the Infrastructure
az deployment group create --template-file resources.bicep --name $DEPLOYMENT_NAME

# Retrieve Deployment Outputs
KEY_VAULT_URI=$(az deployment group show --name $DEPLOYMENT_NAME --query properties.outputs.keyVaultUri.value -o tsv)
WEB_APP_NAME=$(az deployment group show --name $DEPLOYMENT_NAME --query properties.outputs.webAppNameOutput.value -o tsv)

