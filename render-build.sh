#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
