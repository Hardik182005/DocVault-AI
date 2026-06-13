FROM python:3.11-slim

# System deps: tesseract for OCR, poppler for pdf2image, libmagic for MIME checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy sample documents so auto-ingest works on first boot
COPY sample_documents/ ./sample_documents/

# Create storage directories
RUN mkdir -p storage/uploads storage/pages storage/metadata storage/chroma_db

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
