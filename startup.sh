#!/bin/bash
# Install dependencies
pip install -r requirements.txt
# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000