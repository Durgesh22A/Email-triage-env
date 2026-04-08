FROM python:3.12-slim

# Create user with UID 1000 for Hugging Face compatibility
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy and install requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

ENV API_BASE_URL=""
ENV MODEL_NAME=""
ENV HF_TOKEN=""

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]