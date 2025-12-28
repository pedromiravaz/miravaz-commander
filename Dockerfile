FROM python:3.10-slim

WORKDIR /app

# 1. Copy the requirements file first (for better caching)
COPY requirements.txt .

# 2. Install dependencies from the file
# --no-cache-dir keeps the image small
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your application code
COPY main.py .

# 4. (Optional but good practice) Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]