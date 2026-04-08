FROM python:3.11-slim
WORKDIR /app

# Copy absolutely everything from the repo into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the required port
EXPOSE 7860

# Run the newly relocated app.py
CMD ["python", "server/app.py"]