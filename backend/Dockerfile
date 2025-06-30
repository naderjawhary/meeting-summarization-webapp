# Use official PyTorch image with CUDA support
FROM nvcr.io/nvidia/pytorch:24.03-py3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg git tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install torchvision==0.18.0 --extra-index-url https://download.pytorch.org/whl/cu121


# Copy the rest of the project files
COPY . /app/

# Expose Flask default port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
