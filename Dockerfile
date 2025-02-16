FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install uv and use it for installation as recommended
RUN pip install -U uv && \
    uv pip install -r requirements.txt

# Clone Zonos repository and install with uv
RUN git clone --depth 1 https://github.com/Zyphra/Zonos.git /Zonos && \
    cd /Zonos && \
    uv pip install -e . && \
    uv pip install -e .[compile]

# Copy application files
COPY app/ ./app/

EXPOSE 8000

CMD ["python", "-m", "app.main"] 