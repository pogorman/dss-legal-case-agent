#!/usr/bin/env bash
# =============================================================
# DSS Legal Case Agent — Deployment Script
# Provisions Azure resources, deploys database schema/seed,
# builds & deploys Functions, Container App, and SWA.
# =============================================================
set -euo pipefail

# ---- Configuration ----
RESOURCE_GROUP="${RESOURCE_GROUP:?Set RESOURCE_GROUP env var}"
LOCATION="${LOCATION:-eastus}"
SQL_SERVER_NAME="${SQL_SERVER_NAME:?Set SQL_SERVER_NAME env var}"
APIM_NAME="${APIM_NAME:?Set APIM_NAME env var}"
AOAI_ENDPOINT="${AOAI_ENDPOINT:?Set AOAI_ENDPOINT env var}"
AOAI_DEPLOYMENT="${AOAI_DEPLOYMENT:-gpt-4.1}"
ACR_NAME="${ACR_NAME:-}" # Optional: Azure Container Registry for MCP server image

echo "=== DSS Legal Case Agent Deployment ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location:       $LOCATION"
echo "SQL Server:     $SQL_SERVER_NAME"
echo "APIM:           $APIM_NAME"
echo ""

# ---- Step 1: Deploy Bicep infrastructure ----
echo "--- Step 1: Deploying infrastructure (Bicep) ---"
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/main.bicep \
  --parameters \
    existingSqlServerName="$SQL_SERVER_NAME" \
    existingApimName="$APIM_NAME" \
    existingResourceGroupName="$RESOURCE_GROUP" \
    azureOpenAIEndpoint="$AOAI_ENDPOINT" \
    azureOpenAIDeployment="$AOAI_DEPLOYMENT" \
  --output table

# Capture outputs
FUNC_APP_NAME=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.functionAppName.value' -o tsv)
FUNC_PRINCIPAL_ID=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.functionAppPrincipalId.value' -o tsv)
CONTAINER_APP_NAME=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.containerAppName.value' -o tsv)
CONTAINER_PRINCIPAL_ID=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.containerAppPrincipalId.value' -o tsv)
SWA_NAME=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query 'properties.outputs.staticWebAppName.value' -o tsv)

echo "Function App:   $FUNC_APP_NAME"
echo "Container App:  $CONTAINER_APP_NAME"
echo "Static Web App: $SWA_NAME"

# ---- Step 2: Grant Function App managed identity SQL access ----
echo ""
echo "--- Step 2: Granting SQL access to Function App managed identity ---"
echo "Run the following T-SQL on the dss-demo database as an admin:"
echo ""
echo "  CREATE USER [$FUNC_APP_NAME] FROM EXTERNAL PROVIDER;"
echo "  ALTER ROLE db_datareader ADD MEMBER [$FUNC_APP_NAME];"
echo ""
echo "Press Enter after running the SQL commands..."
read -r

# ---- Step 3: Deploy database schema and seed data ----
echo "--- Step 3: Deploy database schema and seed data ---"
echo "Run the following against the dss-demo database:"
echo "  1. database/schema.sql"
echo "  2. database/seed.sql"
echo ""
echo "You can use Azure Data Studio, SSMS, or sqlcmd:"
echo "  sqlcmd -S $SQL_SERVER_NAME.database.windows.net -d dss-demo -G -i database/schema.sql"
echo "  sqlcmd -S $SQL_SERVER_NAME.database.windows.net -d dss-demo -G -i database/seed.sql"
echo ""
echo "Press Enter after deploying the SQL scripts..."
read -r

# ---- Step 4: Build and deploy Azure Functions ----
echo "--- Step 4: Building and deploying Azure Functions ---"
cd functions
npm ci
npm run build
func azure functionapp publish "$FUNC_APP_NAME" --typescript
cd ..

# ---- Step 5: Store Function key in APIM named value ----
echo ""
echo "--- Step 5: APIM Function key ---"
FUNC_KEY=$(az functionapp keys list \
  --name "$FUNC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query 'functionKeys.default' -o tsv 2>/dev/null || echo "")

if [ -n "$FUNC_KEY" ]; then
  echo "Setting APIM named value 'dss-func-key'..."
  az apim nv create \
    --resource-group "$RESOURCE_GROUP" \
    --service-name "$APIM_NAME" \
    --named-value-id "dss-func-key" \
    --display-name "DSS Function Key" \
    --value "$FUNC_KEY" \
    --secret true \
    2>/dev/null || \
  az apim nv update \
    --resource-group "$RESOURCE_GROUP" \
    --service-name "$APIM_NAME" \
    --named-value-id "dss-func-key" \
    --value "$FUNC_KEY" \
    --secret true
else
  echo "WARNING: Could not retrieve Function key. Set 'dss-func-key' named value in APIM manually."
fi

# ---- Step 6: Build and deploy Container App ----
echo ""
echo "--- Step 6: Building and deploying Container App ---"
if [ -n "$ACR_NAME" ]; then
  echo "Building container image in ACR..."
  az acr build \
    --registry "$ACR_NAME" \
    --image dss-case-agent:latest \
    --file mcp-server/Dockerfile \
    mcp-server/

  az containerapp update \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$ACR_NAME.azurecr.io/dss-case-agent:latest"
else
  echo "No ACR_NAME set. Build and push the container image manually:"
  echo "  docker build -t dss-case-agent:latest mcp-server/"
  echo "  docker tag dss-case-agent:latest <acr>.azurecr.io/dss-case-agent:latest"
  echo "  docker push <acr>.azurecr.io/dss-case-agent:latest"
  echo "  az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --image <acr>.azurecr.io/dss-case-agent:latest"
fi

# ---- Step 7: Grant Container App managed identity AOAI access ----
echo ""
echo "--- Step 7: Grant Container App AOAI access ---"
echo "Assign 'Cognitive Services OpenAI User' role to the Container App managed identity:"
echo "  Principal ID: $CONTAINER_PRINCIPAL_ID"
echo ""
echo "  az role assignment create \\"
echo "    --assignee $CONTAINER_PRINCIPAL_ID \\"
echo "    --role 'Cognitive Services OpenAI User' \\"
echo "    --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<aoai-name>"
echo ""

# ---- Step 8: Deploy Static Web App ----
echo "--- Step 8: Deploying Static Web App ---"
SWA_TOKEN=$(az staticwebapp secrets list \
  --name "$SWA_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query 'properties.apiKey' -o tsv 2>/dev/null || echo "")

if [ -n "$SWA_TOKEN" ]; then
  npx -y @azure/static-web-apps-cli deploy web/ \
    --deployment-token "$SWA_TOKEN" \
    --env production
else
  echo "WARNING: Could not get SWA deployment token. Deploy manually:"
  echo "  swa deploy web/ --deployment-token <token>"
fi

# ---- Done ----
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Endpoints:"
echo "  Functions:     https://$(az functionapp show --name $FUNC_APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName -o tsv)/api/cases"
echo "  MCP Server:    $(az deployment group show --resource-group $RESOURCE_GROUP --name main --query 'properties.outputs.containerAppUrl.value' -o tsv)/mcp"
echo "  Web App:       https://$(az deployment group show --resource-group $RESOURCE_GROUP --name main --query 'properties.outputs.staticWebAppUrl.value' -o tsv)"
echo ""
echo "Next steps:"
echo "  1. Update APIM subscription key in Container App secrets"
echo "  2. Configure SWA AAD authentication (tenant ID, client ID)"
echo "  3. Point Copilot Studio agent at the /mcp endpoint"
echo "  4. Test the demo flow"
