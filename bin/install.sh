#! /usr/bin/bash


uv sync
npm ci --include-dev
mkdir static/dist

echo "Installed Correctly!"
