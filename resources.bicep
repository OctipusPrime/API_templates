@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the App Service Plan.')
param appServicePlanName string = 'appServicePlan-${uniqueString(resourceGroup().id)}'

@description('Name of the Azure Web App.')
param webAppName string = 'webApp-${uniqueString(resourceGroup().id)}'

@description('Name of the Azure Key Vault.')
param keyVaultName string = 'keyVault-${uniqueString(resourceGroup().id)}'

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'F1'
  }
  kind: 'linux'
}

// Azure Web App with Managed Identity
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  kind: 'app'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
  }
}

// Azure Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    accessPolicies: [
      // Grant the Web App's Managed Identity access to Key Vault secrets
      {
        tenantId: subscription().tenantId
        objectId: webApp.identity.principalId
        permissions: {
          secrets: [
            'get'
            'list'
          ]
        }
      }
    ]
    // Optional settings
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
  }
}

// Add keyvault uri to the environment variables of the web app
resource webAppConfig 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: webApp
  name: 'appsettings'
  properties: {
    KEY_VAULT_URI: keyVault.properties.vaultUri
  }
}

// Outputs
output keyVaultUri string = keyVault.properties.vaultUri
output webAppNameOutput string = webApp.name
