#!/bin/bash

# Script to create a .env file with required environment variables

# Define the .env filename
ENV_FILE=".env"

# Check if the .env file already exists
if [ -f "$ENV_FILE" ]; then
    echo "✅ '$ENV_FILE' already exists in the current directory."
    exit 0
fi

# Function to prompt user for input with optional default
prompt_input() {
    local var_name=$1
    local prompt_message=$2
    local is_secret=$3
    local default_value=$4
    local input

    if [ -n "$default_value" ]; then
        if [ "$is_secret" = true ]; then
            read -s -p "$prompt_message [Default: $default_value]: " input
            echo
        else
            read -p "$prompt_message [Default: $default_value]: " input
        fi
    else
        if [ "$is_secret" = true ]; then
            read -s -p "$prompt_message: " input
            echo
        else
            read -p "$prompt_message: " input
        fi
    fi

    # If input is empty and a default is provided, use the default
    if [ -z "$input" ] && [ -n "$default_value" ]; then
        echo "$default_value"
        return
    fi

    # If input is empty and no default is provided, prompt again
    while [ -z "$input" ]; do
        echo "❌ $var_name cannot be empty. Please enter a value."
        if [ -n "$default_value" ]; then
            if [ "$is_secret" = true ]; then
                read -s -p "$prompt_message [Default: $default_value]: " input
                echo
            else
                read -p "$prompt_message [Default: $default_value]: " input
            fi
            if [ -z "$input" ]; then
                input="$default_value"
                break
            fi
        else
            if [ "$is_secret" = true ]; then
                read -s -p "$prompt_message: " input
                echo
            else
                read -p "$prompt_message: " input
            fi
        fi
    done

    echo "$input"
}

echo "📄 '$ENV_FILE' not found. Let's create one."

# Prompt for each required environment variable
OPENAI_API_KEY=$(prompt_input "OPENAI_API_KEY" "Enter your OpenAI API Key" false)
DB_HOST=$(prompt_input "DB_HOST" "Enter your Database Host" false "localhost")
DB_USER=$(prompt_input "DB_USER" "Enter your Database User" false)
DB_PASSWORD=$(prompt_input "DB_PASSWORD" "Enter your Database Password" false)
DB_PORT=5432
DB_NAME=$(prompt_input "DB_NAME" "Enter your Database Name" false)

# Create the .env file with the provided inputs
cat <<EOL > $ENV_FILE
OPENAI_API_KEY=$OPENAI_API_KEY
DB_HOST=$DB_HOST
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
EOL

# Set file permissions to read/write for the user only
chmod 777 $ENV_FILE

echo "✅ '$ENV_FILE' has been created successfully with the provided information."

