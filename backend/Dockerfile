FROM python:3.11-slim

# System deps: tesseract for OCR, poppler for pdf2image, libmagic for MIME checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the bundled sample documents made it into the image (fail loudly if not).
RUN echo "=== sample_documents in image ===" && ls -1 /app/sample_documents

RUN mkdir -p storage/uploads storage/pages storage/metadata

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
