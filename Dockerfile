FROM python:3.9-slim

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the files
COPY --chown=user . .

# EXPOSE port 7860 for Hugging Face
EXPOSE 7860

# Updated CMD to point to the new location of app.py
CMD ["python", "server/app.py"]