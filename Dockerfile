FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel

RUN pip install uv

RUN apt update && \
    apt install -y espeak-ng git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone Zonos repository
RUN git clone --depth 1 https://github.com/Zyphra/Zonos.git /Zonos

# Copy our application files
COPY . .

# Install dependencies and Zonos
RUN cd /Zonos && \
    uv pip install --system -e . && \
    uv pip install --system -e .[compile] && \
    uv pip install --system -r /app/requirements.txt

# Make sure Python can find our app module
ENV PYTHONPATH=/app

EXPOSE 8000

# Use absolute path to python
CMD ["/opt/conda/bin/python", "-m", "app.main"] 