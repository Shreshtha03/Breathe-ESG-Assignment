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
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py makemigrations api --noinput || true
python manage.py migrate --noinput

# Seed default analyst user
echo "Creating default analyst user..."
python manage.py create_default_user

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build script execution completed successfully!"
