#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display messages
echo_info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

echo_success() {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

echo_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check if Python 3 is installed
echo_info "Checking if Python3 is installed..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo_success "Python3 is installed: $PYTHON_VERSION"
else
    echo_info "Python3 is not installed. Attempting to install Python3..."
    
    # Detect OS and install Python3 accordingly
    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-pip
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y python3 python3-venv python3-pip
    elif [ "$(uname)" == "Darwin" ]; then
        if command_exists brew; then
            brew update
            brew install python3
        else
            echo_error "Homebrew is not installed. Please install Homebrew first."
            exit 1
        fi
    else
        echo_error "Unsupported OS. Please install Python3 manually."
        exit 1
    fi

    # Verify installation
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version)
        echo_success "Python3 successfully installed: $PYTHON_VERSION"
    else
        echo_error "Python3 installation failed."
        exit 1
    fi
fi

# 2. Check if pip3 is installed
echo_info "Checking if pip3 is installed..."
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version)
    echo_success "pip3 is installed: $PIP_VERSION"
else
    echo_info "pip3 is not installed. Attempting to install pip3..."
    
    # Install pip3 based on OS
    if [ -f /etc/debian_version ]; then
        sudo apt-get install -y python3-pip
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y python3-pip
    elif [ "$(uname)" == "Darwin" ]; then
        brew install pip3
    else
        echo_error "Unsupported OS. Please install pip3 manually."
        exit 1
    fi

    # Verify installation
    if command_exists pip3; then
        PIP_VERSION=$(pip3 --version)
        echo_success "pip3 successfully installed: $PIP_VERSION"
    else
        echo_error "pip3 installation failed."
        exit 1
    fi
fi

# 3. Create a virtual environment
VENV_DIR="venv"
echo_info "Creating a virtual environment in ./$VENV_DIR..."

# Remove existing virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo_info "Virtual environment directory '$VENV_DIR' already exists. Removing it..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
echo_success "Virtual environment '$VENV_DIR' created."

# 4. Activate the virtual environment
echo_info "Activating the virtual environment..."
source "$VENV_DIR/bin/activate"
echo_success "Virtual environment activated."

# Upgrade pip in the virtual environment
echo_info "Upgrading pip in the virtual environment..."
pip install --upgrade pip
echo_success "pip upgraded."

# 5. Install dependencies from requirements.txt
REQUIREMENTS_FILE="requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo_info "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
    echo_success "Dependencies installed."
else
    echo_error "requirements.txt not found in the current directory."
    deactivate
    exit 1
fi

echo_success "Setup complete. Virtual environment is ready to use."

# Optional: Deactivate the virtual environment after setup
# deactivate
