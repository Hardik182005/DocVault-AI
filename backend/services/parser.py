"""
Document parser: handles PDFs, scanned images, plain text.
For every page, produces:
  - extracted text (via pdfplumber or pytesseract OCR)
  - tables as structured list-of-lists (via pdfplumber)
  - rendered page image (via pdf2image) saved to storage/pages/{doc_id}/page_N.png

Resilience: parsing is best-effort and never raises for a recoverable problem.
A single bad page, a failed OCR call, or an unavailable poppler renderer must
not fail the whole document — the page degrades to whatever could be extracted,
and every page is still guaranteed a rendered image so citations always resolve.
"""
import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

# A4-ish blank canvas used whenever a real page image can't be rendered.
_BLANK_SIZE = (800, 1000)


def parse_document(file_path: str, doc_id: str) -> list:
    """
    Returns list of page dicts:
    [{ page_number, text, tables, image_path }]
    Always returns at least one page, even on failure.
    """
    pages_dir = os.path.join(STORAGE_DIR, "pages", doc_id)
    os.makedirs(pages_dir, exist_ok=True)

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".txt":
            return _parse_text_file(file_path, pages_dir)
        elif ext in (".png", ".jpg", ".jpeg"):
            return _parse_image_file(file_path, pages_dir)
        elif ext == ".pdf":
            return _parse_pdf(file_path, pages_dir)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        # Last-resort fallback so an upload is never lost entirely.
        print(f"[PARSER] hard failure on {file_path}: {e} — returning placeholder page")
        image_path = _save_blank(pages_dir, 1)
        return [{
            "page_number": 1,
            "text": f"(Document could not be fully parsed: {e})",
            "tables": [],
            "image_path": image_path,
        }]


def _save_blank(pages_dir: str, page_number: int) -> str:
    """Render a blank placeholder image and return its path."""
    image_path = os.path.join(pages_dir, f"page_{page_number}.png")
    try:
        Image.new("RGB", _BLANK_SIZE, color="white").save(image_path, "PNG")
    except Exception:
        pass
    return image_path


def _ocr(pil_image) -> str:
    """OCR an image, swallowing any tesseract error."""
    try:
        return pytesseract.image_to_string(pil_image, config="--psm 6") or ""
    except Exception as e:
        print(f"[PARSER] OCR failed: {e}")
        return ""


def _render_pdf_images(file_path: str):
    """Render all PDF pages to PIL images; return [] if poppler is unavailable."""
    try:
        return convert_from_path(file_path, dpi=150)
    except Exception as e:
        print(f"[PARSER] pdf2image render failed (poppler?): {e}")
        return []


def _parse_pdf(file_path: str, pages_dir: str) -> list:
    results = []
    page_images = _render_pdf_images(file_path)

    try:
        pdf = pdfplumber.open(file_path)
    except Exception as e:
        print(f"[PARSER] pdfplumber.open failed: {e}")
        pdf = None

    plumber_pages = list(pdf.pages) if pdf else []
    # Drive the loop by whichever source knows the page count.
    page_count = max(len(plumber_pages), len(page_images), 1)

    try:
        for i in range(page_count):
            page_number = i + 1
            plumber_page = plumber_pages[i] if i < len(plumber_pages) else None
            pil_image = page_images[i] if i < len(page_images) else None

            # Always produce a rendered page image.
            image_path = os.path.join(pages_dir, f"page_{page_number}.png")
            if pil_image is not None:
                try:
                    pil_image.save(image_path, "PNG")
                except Exception:
                    image_path = _save_blank(pages_dir, page_number)
            else:
                image_path = _save_blank(pages_dir, page_number)

            # Text: pdfplumber first, OCR fallback when sparse.
            text = ""
            if plumber_page is not None:
                try:
                    text = plumber_page.extract_text() or ""
                except Exception as e:
                    print(f"[PARSER] extract_text failed p{page_number}: {e}")
            if len(text.strip()) < 50 and pil_image is not None:
                ocr_text = _ocr(pil_image)
                if len(ocr_text.strip()) > len(text.strip()):
                    text = ocr_text

            # Tables (best-effort).
            tables = []
            if plumber_page is not None:
                try:
                    raw_tables = plumber_page.extract_tables()
                    tables = [t for t in raw_tables if t] if raw_tables else []
                except Exception as e:
                    print(f"[PARSER] extract_tables failed p{page_number}: {e}")

            results.append({
                "page_number": page_number,
                "text": text.strip(),
                "tables": tables,
                "image_path": image_path,
            })
    finally:
        if pdf is not None:
            try:
                pdf.close()
            except Exception:
                pass

    return results or [{
        "page_number": 1,
        "text": "",
        "tables": [],
        "image_path": _save_blank(pages_dir, 1),
    }]


def _parse_image_file(file_path: str, pages_dir: str) -> list:
    image_path = os.path.join(pages_dir, "page_1.png")
    text = ""
    try:
        img = Image.open(file_path)
        try:
            img.save(image_path, "PNG")
        except Exception:
            image_path = _save_blank(pages_dir, 1)
        text = _ocr(img)
    except Exception as e:
        print(f"[PARSER] image open failed: {e}")
        image_path = _save_blank(pages_dir, 1)
    return [{"page_number": 1, "text": text.strip(), "tables": [], "image_path": image_path}]


def _parse_text_file(file_path: str, pages_dir: str) -> list:
    content = ""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"[PARSER] text read failed: {e}")
    image_path = _save_blank(pages_dir, 1)
    return [{"page_number": 1, "text": content, "tables": [], "image_path": image_path}]
