#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up external binaries..."
mkdir -p bin

# 1. FFmpeg (with user-agent and fallback)
if [ ! -f "bin/ffmpeg" ]; then
    echo "Downloading static FFmpeg..."
    cd bin
    (wget -q -U "Mozilla/5.0" https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz || curl -sSL -A "Mozilla/5.0" -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz) || true
    if [ -f "ffmpeg-release-amd64-static.tar.xz" ]; then
        tar xf ffmpeg-release-amd64-static.tar.xz || true
        mv ffmpeg-*-amd64-static/ffmpeg . 2>/dev/null || true
        mv ffmpeg-*-amd64-static/ffprobe . 2>/dev/null || true
        rm -rf ffmpeg-*-amd64-static*
    fi
    cd ..
fi

# 2. Node.js
if [ ! -f "bin/node" ]; then
    echo "Downloading Node.js..."
    cd bin
    (wget -q https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz || curl -sSL -O https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz) || true
    if [ -f "node-v20.10.0-linux-x64.tar.xz" ]; then
        tar xf node-v20.10.0-linux-x64.tar.xz || true
        mv node-v20.10.0-linux-x64/bin/node . 2>/dev/null || true
        rm -rf node-v20.10.0-linux-x64*
    fi
    cd ..
fi

# 3. Deno
if [ ! -f "bin/deno" ]; then
    echo "Downloading Deno..."
    cd bin
    (wget -q https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip || curl -sSL -O https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip) || true
    if [ -f "deno-x86_64-unknown-linux-gnu.zip" ]; then
        python3 -c "import zipfile; zipfile.ZipFile('deno-x86_64-unknown-linux-gnu.zip').extractall('.')" 2>/dev/null || true
        rm -f deno-x86_64-unknown-linux-gnu.zip
    fi
    cd ..
fi

chmod +x bin/* 2>/dev/null || true
echo "Build completed successfully!"
