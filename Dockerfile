FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY env.py .
COPY openenv.yaml .
COPY server.py .
EXPOSE 7860
CMD ["python", "server.py"]