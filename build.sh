#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Build Frontend
echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Setup Django Backend
echo "Setting up Django backend..."
cd backend

# Activate virtualenv if it exists on Render
if [ -d "../.venv" ]; then
    echo "Activating Render virtual environment..."
    source ../.venv/bin/activate
fi

pip install -r requirements.txt

# Run migrations (only makemigrations during build to compile migration files)
echo "Generating migration files..."
python manage.py makemigrations api --noinput || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build script execution completed successfully!"
