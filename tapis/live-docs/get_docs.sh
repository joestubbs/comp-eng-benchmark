# Download all of the files 
wget https://raw.githubusercontent.com/TACC/abaco/dev-v3/docs/specs/openapi_v3.yml -O abaco.yml
wget https://raw.githubusercontent.com/tapis-project/openapi-apps/prod/AppsAPI.yaml
wget https://raw.githubusercontent.com/tapis-project/authenticator/prod/service/resources/openapi_v3.yml -O authenticator.yml
wget https://raw.githubusercontent.com/tapis-project/openapi-files/prod/FilesAPI.yaml
wget https://raw.githubusercontent.com/tapis-project/tapis-client-java/prod/jobs-client/src/main/resources/JobsAPI.yaml
wget https://raw.githubusercontent.com/tapis-project/tapis-client-java/prod/meta-client/src/main/resources/metav3-openapi.yaml
wget https://raw.githubusercontent.com/tapis-project/openapi-notifications/prod/NotificationsAPI.yaml
wget https://raw.githubusercontent.com/TACC/paas/prod/pgrest/resources/openapi_v3.yml -O pgrest.yaml
wget https://raw.githubusercontent.com/tapis-project/pods_service/main/docs/openapi_v3-pods.yml -O pods.yml
wget https://raw.githubusercontent.com/tapis-project/openapi-security/prod/SkAPI.yaml
wget https://raw.githubusercontent.com/tapis-project/streams-api/prod/service/resources/openapi_v3.yml -O streams.yml
wget https://raw.githubusercontent.com/tapis-project/openapi-systems/prod/SystemsAPI.yaml
wget https://raw.githubusercontent.com/tapis-project/tenants-api/prod/service/resources/openapi_v3.yml -O tenants.yml
wget https://raw.githubusercontent.com/tapis-project/tokens-api/prod/service/resources/openapi_v3.yml -O tokens.yml
wget https://raw.githubusercontent.com/tapis-project/tapis-workflows/prod/src/api/specs/WorkflowsAPI.yaml

# Concat all of the files into a single text file 
cat actors.yml AppsAPI.yaml authenticator.yml FilesAPI.yaml JobsAPI.yaml metav3-openapi.yaml NotificationsAPI.yaml pgrest.yaml pods.yml SkAPI.yaml streams.yml SystemsAPI.yaml tenants.yml tokens.yml WorkflowsAPI.yaml > All_Tapis_OpenAPI_Specs.txt