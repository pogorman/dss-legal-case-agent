// =============================================================
// DSS Legal Case Agent — Infrastructure
// Provisions: SQL DB, Function App, Container App, SWA, APIM API
// =============================================================

@description('Name of the existing SQL Server')
param existingSqlServerName string

@description('Name of the existing APIM instance')
param existingApimName string

@description('Name of the existing resource group')
param existingResourceGroupName string

@description('Name of the existing VNet (for Function App VNet integration and private endpoints)')
param existingVnetName string

@description('Subnet name for Function App VNet integration')
param functionSubnetName string = 'snet-dss-functions'

@description('Subnet name for private endpoints')
param privateEndpointSubnetName string = 'snet-private-endpoints'

@description('Azure OpenAI endpoint URL')
param azureOpenAIEndpoint string

@description('Azure OpenAI deployment name')
param azureOpenAIDeployment string = 'gpt-4.1'

@description('Location for new resources')
param location string = resourceGroup().location

@description('Container image for the MCP server')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

// =============================================================
// Existing VNet & Subnets
// =============================================================
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' existing = {
  name: existingVnetName
}

resource funcSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' existing = {
  parent: vnet
  name: functionSubnetName
}

resource peSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' existing = {
  parent: vnet
  name: privateEndpointSubnetName
}

// =============================================================
// Azure SQL Database
// =============================================================
resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' existing = {
  name: existingSqlServerName
}

resource sqlDb 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: 'dss-demo'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 2147483648
  }
}

// =============================================================
// Private Endpoint for SQL Server
// The SQL server has publicNetworkAccess: Disabled.
// This private endpoint + DNS zone allows VNet-integrated
// resources (Function App) to reach SQL over the private network.
// =============================================================
resource sqlPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = {
  name: 'pe-sql-philly'
  location: location
  properties: {
    subnet: {
      id: peSubnet.id
    }
    privateLinkServiceConnections: [
      {
        name: 'pe-sql-philly'
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: ['sqlServer']
        }
      }
    ]
  }
}

resource sqlPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.database.windows.net'
  location: 'global'
}

resource sqlPrivateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: sqlPrivateDnsZone
  name: '${existingVnetName}-link'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
}

resource sqlPrivateEndpointDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-09-01' = {
  parent: sqlPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-database-windows-net'
        properties: {
          privateDnsZoneId: sqlPrivateDnsZone.id
        }
      }
    ]
  }
}

// =============================================================
// Function App (Flex Consumption)
// =============================================================
resource funcStorageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stdssdemo${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource funcPlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: 'plan-dss-demo-func'
  location: location
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  kind: 'functionapp'
  properties: {
    reserved: true
  }
}

resource funcApp 'Microsoft.Web/sites@2023-01-01' = {
  name: 'dss-demo-func'
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: funcPlan.id
    virtualNetworkSubnetId: funcSubnet.id
    siteConfig: {
      appSettings: [
        { name: 'AzureWebJobsStorage__accountName', value: funcStorageAccount.name }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'node' }
        { name: 'WEBSITE_NODE_DEFAULT_VERSION', value: '~20' }
        { name: 'SQL_SERVER', value: '${existingSqlServerName}.database.windows.net' }
        { name: 'SQL_DATABASE', value: 'dss-demo' }
      ]
      linuxFxVersion: 'NODE|20'
      vnetRouteAllEnabled: true
    }
  }
}

// =============================================================
// Container App Environment & Container App
// =============================================================
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-dss-case-agent'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-11-02-preview' = {
  name: 'env-dss-case-agent'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2023-11-02-preview' = {
  name: 'dss-case-agent'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
      }
      secrets: [
        { name: 'apim-subscription-key', value: 'REPLACE_WITH_APIM_KEY' }
      ]
    }
    template: {
      containers: [
        {
          name: 'dss-case-agent'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'APIM_BASE_URL', value: 'https://${existingApimName}.azure-api.net/dss' }
            { name: 'APIM_SUBSCRIPTION_KEY', secretRef: 'apim-subscription-key' }
            { name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenAIEndpoint }
            { name: 'AZURE_OPENAI_DEPLOYMENT', value: azureOpenAIDeployment }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

// =============================================================
// Static Web App
// =============================================================
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: 'swa-dss-legal-case'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {}
}

// =============================================================
// APIM: Product, API, and Operations
// =============================================================
resource apim 'Microsoft.ApiManagement/service@2023-05-01-preview' existing = {
  name: existingApimName
}

resource apimProduct 'Microsoft.ApiManagement/service/products@2023-05-01-preview' = {
  parent: apim
  name: 'dss-demo'
  properties: {
    displayName: 'DSS Demo'
    description: 'Product for DSS Legal Case Agent demo'
    subscriptionRequired: true
    approvalRequired: false
    state: 'published'
  }
}

resource apimApi 'Microsoft.ApiManagement/service/apis@2023-05-01-preview' = {
  parent: apim
  name: 'dss-case-api'
  properties: {
    displayName: 'DSS Case API'
    description: 'API for DSS Legal Case Agent — 5 case query endpoints'
    serviceUrl: 'https://${funcApp.properties.defaultHostName}/api'
    path: 'dss'
    protocols: ['https']
    subscriptionKeyParameterNames: {
      header: 'Ocp-Apim-Subscription-Key'
      query: 'subscription-key'
    }
  }
}

// API Operations
resource opListCases 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'list-cases'
  properties: {
    displayName: 'List Cases'
    method: 'GET'
    urlTemplate: '/cases'
  }
}

resource opGetCase 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'get-case-summary'
  properties: {
    displayName: 'Get Case Summary'
    method: 'GET'
    urlTemplate: '/cases/{caseId}'
    templateParameters: [
      { name: 'caseId', type: 'string', required: true }
    ]
  }
}

resource opGetTimeline 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'get-timeline'
  properties: {
    displayName: 'Get Timeline'
    method: 'GET'
    urlTemplate: '/cases/{caseId}/timeline'
    templateParameters: [
      { name: 'caseId', type: 'string', required: true }
    ]
  }
}

resource opGetStatements 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'get-statements'
  properties: {
    displayName: 'Get Statements'
    method: 'GET'
    urlTemplate: '/cases/{caseId}/statements'
    templateParameters: [
      { name: 'caseId', type: 'string', required: true }
    ]
  }
}

resource opGetDiscrepancies 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'get-discrepancies'
  properties: {
    displayName: 'Get Discrepancies'
    method: 'GET'
    urlTemplate: '/cases/{caseId}/discrepancies'
    templateParameters: [
      { name: 'caseId', type: 'string', required: true }
    ]
  }
}

// APIM Policy: inject x-functions-key on all operations
resource apimApiPolicy 'Microsoft.ApiManagement/service/apis/policies@2023-05-01-preview' = {
  parent: apimApi
  name: 'policy'
  properties: {
    value: '''
      <policies>
        <inbound>
          <base />
          <set-header name="x-functions-key" exists-action="override">
            <value>{{dss-func-key}}</value>
          </set-header>
        </inbound>
        <backend><base /></backend>
        <outbound><base /></outbound>
        <on-error><base /></on-error>
      </policies>
    '''
    format: 'xml'
  }
}

// Link API to product
resource apimProductApi 'Microsoft.ApiManagement/service/products/apis@2023-05-01-preview' = {
  parent: apimProduct
  name: 'dss-case-api'
}

// =============================================================
// Outputs
// =============================================================
output sqlDatabaseName string = sqlDb.name
output functionAppName string = funcApp.name
output functionAppHostname string = funcApp.properties.defaultHostName
output functionAppPrincipalId string = funcApp.identity.principalId
output containerAppName string = containerApp.name
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output containerAppPrincipalId string = containerApp.identity.principalId
output staticWebAppName string = staticWebApp.name
output staticWebAppUrl string = staticWebApp.properties.defaultHostname
