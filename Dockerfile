FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel

WORKDIR /app

# Add conda to PATH
ENV PATH /opt/conda/bin:$PATH

RUN apt update && \
    apt install -y espeak-ng git && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/Zyphra/Zonos.git /Zonos

COPY . .

RUN pip install -r requirements.txt && \
    cd /Zonos && \
    pip install -e .

ENV PYTHONPATH=/app

EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\npython main.py' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Use the entrypoint script
CMD ["/entrypoint.sh"] 