# app.py
from router import classify_document, route_document
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import shutil
import joblib
import pdfplumber
from PIL import Image
import pytesseract
from io import BytesIO

MODEL_PATH = "models/doc_clf.joblib"
STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Simple routing rules mapping doc_type -> department
ROUTING_RULES = {
    "invoice": "finance",
    "report": "finance",
    "contract": "admin",
    "resume": "admin",
}
CONFIDENCE_THRESHOLD = 0.6  # below this -> Manual Review

app = FastAPI(title="IDMS Mini Classifier & Router")

# Load model
clf = joblib.load(MODEL_PATH)


def extract_text_from_pdf_bytes(b: bytes) -> str:
    text_parts = []
    try:
        # try pdfplumber native text extraction
        with pdfplumber.open(BytesIO(b)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
    except Exception:
        pass
    # if text_parts empty, fall back to OCR of pages as images
    if not text_parts:
        try:
            from pdf2image import convert_from_bytes
            pages = convert_from_bytes(b)
            for p in pages:
                text_parts.append(pytesseract.image_to_string(p))
        except Exception:
            # last fallback: try OCR on raw bytes as image
            try:
                img = Image.open(BytesIO(b))
                text_parts.append(pytesseract.image_to_string(img))
            except Exception:
                pass
    return "\n".join(text_parts)


def extract_text_from_image_bytes(b: bytes) -> str:
    try:
        img = Image.open(BytesIO(b))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def save_upload(file: UploadFile):
    safe_name = file.filename
    path = os.path.join(STORAGE_DIR, safe_name)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path


@app.post("/ingest")
async def ingest(file: UploadFile = File(None), text: str = Form(None)):
    """
    Accepts either an uploaded file (pdf, image) OR form field 'text' containing doc text.
    Returns predicted class, probability, and routing decision.
    """
    if file is None and not text:
        return JSONResponse({"error": "Provide either a file or text"}, status_code=400)

    extracted_text = ""
    saved_path = None
    if file:
        saved_path = save_upload(file)
        data = open(saved_path, "rb").read()
        mime = file.content_type.lower()
        if "pdf" in mime:
            extracted_text = extract_text_from_pdf_bytes(data)
        elif mime.startswith("image/") or saved_path.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
            extracted_text = extract_text_from_image_bytes(data)
        else:
            # try to read bytes as text
            try:
                extracted_text = data.decode(errors="ignore")
            except Exception:
                extracted_text = ""
    else:
        extracted_text = text

    if not extracted_text.strip():
        return JSONResponse({"error": "Could not extract text"}, status_code=422)

    # predict
    proba = None
    pred = None
    try:
        probs = clf.predict_proba([extracted_text])[0]
        class_idx = probs.argmax()
        pred = clf.classes_[class_idx]
        proba = float(probs[class_idx])
    except Exception:
        # fallback to predict (no probabilities)
        pred = clf.predict([extracted_text])[0]
        proba = None

    # routing decision
    if proba is not None and proba < CONFIDENCE_THRESHOLD:
        route = "manual_review"
        note = "low_confidence"
    else:
        route = ROUTING_RULES.get(pred, "manual_review")
        note = "rule_mapping"

    resp = {
        "predicted_label": pred,
        "probability": proba,
        "route_to": route,
        "note": note,
        "storage_path": saved_path
    }
    return JSONResponse(resp)


def process_new_document(document_path):
    print("Classifying document...")
    doc_type = classify_document(document_path)
    print(f"Detected document type: {doc_type}")

    print("Routing document to department emails...")
    result = route_document(doc_type, document_path)

    print("Routing complete.")
    print(result)


if __name__ == "__main__":
    # Test using one of your storage PDFs
    document_path = "storage/invoice.pdf"
    process_new_document(document_path)
