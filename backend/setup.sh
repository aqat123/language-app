#!/bin/bash

# This script sets up the Python virtual environment and installs dependencies.

# Define the virtual environment directory name
VENV_DIR="venv"

# Function to print error messages and exit
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Main setup logic
main() {
    echo "Starting backend setup..."

    # 1. Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        error_exit "python3 could not be found. Please install Python 3."
    fi

    # 2. Create the virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating Python virtual environment in './$VENV_DIR'..."
        python3 -m venv "$VENV_DIR" || error_exit "Failed to create virtual environment."
    else
        echo "Virtual environment already exists."
    fi

    # 3. Activate the virtual environment and install dependencies
    echo "Activating virtual environment and installing dependencies from requirements.txt..."
    source "$VENV_DIR/bin/activate" && pip install -r requirements.txt || error_exit "Failed to install dependencies."

    echo ""
    echo "✅ Setup complete!"
    echo "To activate the virtual environment manually, run:"
    echo "source $VENV_DIR/bin/activate"
}

# Run the main function
main
