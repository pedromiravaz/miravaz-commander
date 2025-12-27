FROM python:3.10-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic
COPY main.py .