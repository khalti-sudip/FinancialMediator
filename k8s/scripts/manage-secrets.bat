@echo off
echo Generating secure secrets...

REM Generate or read existing secrets
set /p db_password="Enter database password (leave blank to generate): "
if "%db_password%"=="" (
    set db_password=%RANDOM%%RANDOM%%RANDOM%%RANDOM%
)

set /p django_secret="Enter Django secret key (leave blank to generate): "
if "%django_secret%"=="" (
    set django_secret=%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%
)

set /p email_password="Enter email password (leave blank to generate): "
if "%email_password%"=="" (
    set email_password=%RANDOM%%RANDOM%%RANDOM%
)

set /p aws_access_key="Enter AWS access key (leave blank to generate): "
if "%aws_access_key%"=="" (
    set aws_access_key=%RANDOM%%RANDOM%%RANDOM%
)

set /p aws_secret_key="Enter AWS secret key (leave blank to generate): "
if "%aws_secret_key%"=="" (
    set aws_secret_key=%RANDOM%%RANDOM%%RANDOM%%RANDOM%
)

echo Updating values.yaml with new secrets...

REM Update values.yaml with new secrets
powershell -Command "(Get-Content k8s/values.yaml) -replace 'databasePassword:.*', 'databasePassword: %db_password%' | Set-Content k8s/values.yaml"
powershell -Command "(Get-Content k8s/values.yaml) -replace 'djangoSecretKey:.*', 'djangoSecretKey: %django_secret%' | Set-Content k8s/values.yaml"
powershell -Command "(Get-Content k8s/values.yaml) -replace 'emailPassword:.*', 'emailPassword: %email_password%' | Set-Content k8s/values.yaml"
powershell -Command "(Get-Content k8s/values.yaml) -replace 'awsAccessKey:.*', 'awsAccessKey: %aws_access_key%' | Set-Content k8s/values.yaml"
powershell -Command "(Get-Content k8s/values.yaml) -replace 'awsSecretKey:.*', 'awsSecretKey: %aws_secret_key%' | Set-Content k8s/values.yaml"

echo Secrets have been updated in values.yaml
echo Please commit the changes to git
