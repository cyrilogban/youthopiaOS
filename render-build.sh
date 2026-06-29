#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Downloading static FFmpeg..."
mkdir -p bin
cd bin
wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg-release-amd64-static.tar.xz
mv ffmpeg-*-amd64-static/ffmpeg .
mv ffmpeg-*-amd64-static/ffprobe .
rm -rf ffmpeg-*-amd64-static*
cd ..

echo "Installing Python dependencies..."
pip install -r requirements.txt
