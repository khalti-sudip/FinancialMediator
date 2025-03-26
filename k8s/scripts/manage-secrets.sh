#!/bin/bash

# Function to generate a secure random string
function generate_secret() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d '=' | tr '/+' '_-'
}

# Function to encrypt a value using sops
function encrypt_value() {
    local value=$1
    echo -n "$value" | sops --encrypt --in-type "text" --out-type "yaml" --encrypted-regex ".*" -
}

# Generate or read existing secrets
read -p "Enter database password (leave blank to generate): " db_password
read -p "Enter Django secret key (leave blank to generate): " django_secret
read -p "Enter email password (leave blank to generate): " email_password
read -p "Enter AWS access key (leave blank to generate): " aws_access_key
read -p "Enter AWS secret key (leave blank to generate): " aws_secret_key

# Generate missing secrets
if [ -z "$db_password" ]; then
    db_password=$(generate_secret 32)
fi

if [ -z "$django_secret" ]; then
    django_secret=$(generate_secret 50)
fi

if [ -z "$email_password" ]; then
    email_password=$(generate_secret 24)
fi

if [ -z "$aws_access_key" ]; then
    aws_access_key=$(generate_secret 20)
fi

if [ -z "$aws_secret_key" ]; then
    aws_secret_key=$(generate_secret 40)
fi

# Encrypt and update values.yaml
sed -i "/databasePassword:/c\  databasePassword: $(encrypt_value "$db_password")" k8s/values.yaml
sed -i "/djangoSecretKey:/c\  djangoSecretKey: $(encrypt_value "$django_secret")" k8s/values.yaml
sed -i "/emailPassword:/c\  emailPassword: $(encrypt_value "$email_password")" k8s/values.yaml
sed -i "/awsAccessKey:/c\  awsAccessKey: $(encrypt_value "$aws_access_key")" k8s/values.yaml
sed -i "/awsSecretKey:/c\  awsSecretKey: $(encrypt_value "$aws_secret_key")" k8s/values.yaml

echo "Secrets have been updated and encrypted in values.yaml"
echo "Please commit the changes to git"
