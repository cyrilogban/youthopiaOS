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
echo "Downloading Node.js (for yt-dlp signature extraction)..."
wget -q https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz
tar xf node-v20.10.0-linux-x64.tar.xz
mv node-v20.10.0-linux-x64/bin/node .
rm -rf node-v20.10.0-linux-x64*
cd ..

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Ensure binaries have executable permissions
chmod +x bin/node bin/ffmpeg bin/ffprobe

