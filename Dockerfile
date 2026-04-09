FROM python:3.11-slim
WORKDIR /app

# 1. Install system dependencies if needed
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 2. Copy the configuration files first to cache layers
COPY pyproject.toml uv.lock requirements.txt ./

# 3. Install dependencies (including the 'uv' installer for speed)
RUN pip install --no-cache-dir uv && uv pip install --system -r requirements.txt

# 4. Copy the rest of the code
COPY . .

# 5. Install the local project in editable mode so 'server' is recognized
RUN pip install -e .

# 6. Expose the port
EXPOSE 7860

# 7. Start the server using the module path
CMD ["python", "-m", "server.app"]