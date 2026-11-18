FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Seed initial database
RUN python database/seed_data.py

# Expose port
EXPOSE 8000

# Start ASGI application server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
