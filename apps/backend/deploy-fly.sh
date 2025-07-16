#!/bin/bash
# Fly.io Deployment Script for Vessel Guard Backend

echo "Starting Fly.io deployment for Vessel Guard Backend..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "Error: flyctl is not installed. Please install it first:"
    echo "curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if we're logged into Fly.io
if ! flyctl auth whoami &> /dev/null; then
    echo "Error: Not logged into Fly.io. Please run 'flyctl auth login' first."
    exit 1
fi

echo "Logged in as: $(flyctl auth whoami)"

# Check if fly.toml exists
if [ ! -f "fly.toml" ]; then
    echo "Error: fly.toml not found. Please ensure you're in the correct directory."
    exit 1
fi

# Create Fly.io app if it doesn't exist
echo "Checking if Fly.io app exists..."
if ! flyctl apps list | grep -q "vessel-guard-backend"; then
    echo "Creating Fly.io app..."
    flyctl apps create vessel-guard-backend --org personal
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create Fly.io app."
        exit 1
    fi
fi

# Set secrets from .env.fly
echo "Setting Fly.io secrets..."
if [ -f ".env.fly" ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ $key =~ ^[[:space:]]*# ]] || [[ -z $key ]]; then
            continue
        fi
        
        # Skip certain variables that shouldn't be secrets
        if [[ $key == "APP_NAME" || $key == "ENVIRONMENT" || $key == "FLY_APP_NAME" || $key == "FLY_REGION" ]]; then
            continue
        fi
        
        echo "Setting secret: $key"
        flyctl secrets set "$key=$value" --app vessel-guard-backend
    done < .env.fly
fi

# Create PostgreSQL database if it doesn't exist
echo "Checking for PostgreSQL database..."
if ! flyctl postgres list | grep -q "vessel-guard-db"; then
    echo "Creating PostgreSQL database..."
    flyctl postgres create --name vessel-guard-db --region sea --vm-size shared-cpu-1x --volume-size 3
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create PostgreSQL database."
        exit 1
    fi
    
    # Attach database to app
    echo "Attaching database to app..."
    flyctl postgres attach vessel-guard-db --app vessel-guard-backend
fi

# Deploy the application
echo "Deploying application..."
flyctl deploy --app vessel-guard-backend

if [ $? -eq 0 ]; then
    echo "Deployment successful!"
    echo "Your app is available at: https://vessel-guard-backend.fly.dev"
    
    # Show app status
    echo "App status:"
    flyctl status --app vessel-guard-backend
else
    echo "Deployment failed!"
    exit 1
fi

echo "Fly.io deployment completed!"
