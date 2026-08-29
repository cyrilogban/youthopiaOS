#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ -d "miniapp" ]; then
  echo "Building YouThopiaOS Mini App frontend..."
  cd miniapp
  npm install
  npm run build
  cd ..
fi

echo "Build completed successfully!"
