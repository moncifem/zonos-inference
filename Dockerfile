FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN pip install -U uv

# Copy application files
COPY requirements.txt app.py ./

# Install Python dependencies using uv
RUN uv pip install --no-cache-dir -r requirements.txt

# Install Zonos
RUN uv pip install -e .

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 