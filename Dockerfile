FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV API_BASE_URL=""
ENV MODEL_NAME=""
ENV HF_TOKEN=""
EXPOSE 7860
CMD ["python3", "app.py"]
