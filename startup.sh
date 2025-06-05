#!/usr/bin/env bash

echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = \$PORT\n\
" > ~/.streamlit/config.toml

echo "Starting Streamlit on port \$PORT..."
streamlit run app.py --server.address 0.0.0.0 --server.port=8000



