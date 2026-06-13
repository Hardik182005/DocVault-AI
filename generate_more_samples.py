"""
generate_more_samples.py -- generates 5 additional synthetic documents.
Covers: legal contract, HR policy, purchase order, product spec, NDA.
Usage: python generate_more_samples.py
"""
import os
from fpdf import FPDF

os.makedirs("sample_documents", exist_ok=True)


def new_pdf() -> FPDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    return pdf


# ── 1. Employment Contract ────────────────────────────────────────────────────
def create_employment_contract():
    pdf = new_pdf()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "EMPLOYMENT CONTRACT", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "This agreement is entered into as of 1st December 2024", ln=True, align="C")
    pdf.ln(4)

    sections = [
        ("PARTIES",
         "Employer: BFAI Technologies Pvt Ltd, Suite 7, Tech Tower, Bengaluru 560001 (hereinafter 'Company').\n"
         "Employee: Ms. Ananya Sharma, 14 Rose Garden, Pune 411001 (hereinafter 'Employee')."),
        ("POSITION & DUTIES",
         "The Employee is engaged as Senior Machine Learning Engineer (Level L4). "
         "The Employee shall report to the VP of Engineering and perform duties including: "
         "designing and training large-scale document understanding models; "
         "maintaining production RAG pipelines; "
         "mentoring junior engineers; and contributing to technical roadmap planning."),
        ("COMPENSATION",
         "Base Salary: INR 28,00,000 per annum (paid monthly).\n"
         "Performance Bonus: Up to 20% of base salary, assessed annually in April.\n"
         "ESOPs: 2,500 options vesting over 4 years (1-year cliff, monthly thereafter).\n"
         "Joining Bonus: INR 2,00,000 (repayable if resignation within 12 months)."),
        ("BENEFITS",
         "Health Insurance: Family floater policy of INR 10 lakh (Company-funded).\n"
         "Provident Fund: 12% employer contribution.\n"
         "Leave: 24 earned leaves + 12 casual leaves per calendar year.\n"
         "Work Mode: Hybrid -- 3 days in-office (Mon, Tue, Thu), 2 days remote."),
        ("CONFIDENTIALITY & IP",
         "The Employee agrees that all inventions, code, models, and datasets created during "
         "employment are the exclusive property of the Company. The Employee shall not disclose "
         "any trade secrets, client data, or proprietary algorithms during or after employment. "
         "This clause survives termination for a period of 3 years."),
        ("TERMINATION",
         "Either party may terminate with 90 days written notice. The Company may terminate "
         "immediately for cause (fraud, gross misconduct, breach of confidentiality). "
         "Upon termination, the Employee must return all company equipment and delete all "
         "proprietary data within 5 business days."),
        ("GOVERNING LAW",
         "This agreement is governed by the laws of India. Any disputes shall be settled by "
         "arbitration in Bengaluru under the Arbitration and Conciliation Act 1996."),
    ]

    for title, body in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(3)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 6, "For BFAI Technologies Pvt Ltd:", border=0)
    pdf.cell(90, 6, "Employee:", border=0, ln=True)
    pdf.ln(10)
    pdf.cell(90, 6, "___________________________", border=0)
    pdf.cell(90, 6, "___________________________", border=0, ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(90, 5, "Rohit Verma, CEO", border=0)
    pdf.cell(90, 5, "Ms. Ananya Sharma", border=0, ln=True)
    pdf.cell(90, 5, "Date: 01/12/2024", border=0)
    pdf.cell(90, 5, "Date: 01/12/2024", border=0, ln=True)

    pdf.output("sample_documents/employment_contract.pdf")
    print("[OK] employment_contract.pdf")


# ── 2. HR Policy Manual ───────────────────────────────────────────────────────
def create_hr_policy():
    pdf = new_pdf()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "BFAI Technologies -- HR Policy Manual", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Version 3.1  |  Effective Date: 1 January 2025  |  Internal Use Only", ln=True, align="C")
    pdf.ln(6)

    policies = [
        ("1. Code of Conduct",
         "All employees must maintain professional behaviour, respect colleagues, and avoid "
         "conflicts of interest. Harassment, discrimination, or intimidation of any kind will "
         "result in immediate disciplinary action including termination. Employees must declare "
         "any personal relationships with direct reports to HR within 30 days."),
        ("2. Working Hours & Flexibility",
         "Core hours: 10:00 AM to 5:00 PM IST. Employees may flex start/end times within "
         "a 2-hour window subject to team agreement. A 45-minute lunch break is mandated. "
         "Overtime beyond 48 hours per week requires VP approval and is compensated at 1.5x rate."),
        ("3. Leave Policy",
         "Earned Leave (EL): 24 days per year, accrued at 2 days/month. Maximum carry-forward: 30 days.\n"
         "Casual Leave (CL): 12 days per year, non-carry-forward.\n"
         "Sick Leave (SL): 10 days per year with medical certificate for absences > 3 days.\n"
         "Maternity Leave: 26 weeks fully paid (per Maternity Benefit Act 2017).\n"
         "Paternity Leave: 10 days fully paid.\n"
         "Bereavement Leave: 5 days for immediate family."),
        ("4. Performance Review Process",
         "Reviews are conducted bi-annually (April and October). The framework uses OKRs set "
         "at the start of each half-year. Ratings: Exceptional (5), Exceeds Expectations (4), "
         "Meets Expectations (3), Needs Improvement (2), Unsatisfactory (1). "
         "Ratings below 3 for two consecutive cycles trigger a Performance Improvement Plan (PIP)."),
        ("5. Travel & Expense Policy",
         "Business travel requires prior approval from the employee's manager and Finance. "
         "Economy class for domestic flights; business class for international flights > 6 hours. "
         "Hotel cap: INR 6,000/night domestic, USD 150/night international. "
         "Meal allowance: INR 800/day domestic. All claims must be submitted within 15 days with receipts."),
        ("6. Data Security & Device Policy",
         "Company-issued laptops must have full-disk encryption enabled. Personal devices may not "
         "store client or proprietary data. VPN is mandatory when accessing internal systems remotely. "
         "Employees must report lost/stolen devices within 2 hours. "
         "AI tools (ChatGPT, Copilot) must not process confidential company or client data."),
        ("7. Grievance Redressal",
         "Employees may raise grievances via the HR portal or directly with the POSH committee. "
         "All complaints are acknowledged within 48 hours and investigated within 30 days. "
         "Anonymous reporting is supported via the Ethics Hotline: ethics@bfai.in."),
    ]

    for title, body in policies:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(3)

    pdf.output("sample_documents/hr_policy_manual.pdf")
    print("[OK] hr_policy_manual.pdf")


# ── 3. Purchase Order ─────────────────────────────────────────────────────────
def create_purchase_order():
    pdf = new_pdf()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "PURCHASE ORDER", ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 6, "Purchase Order Number:", border=0)
    pdf.cell(90, 6, "PO-2024-1187", border=0, ln=True)
    pdf.cell(90, 6, "PO Date:", border=0)
    pdf.cell(90, 6, "20 November 2024", border=0, ln=True)
    pdf.cell(90, 6, "Expected Delivery:", border=0)
    pdf.cell(90, 6, "10 December 2024", border=0, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 7, "Bill To:", border=0)
    pdf.cell(90, 7, "Vendor:", border=0, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(90, 5, "BFAI Technologies Pvt Ltd", border=0)
    pdf.cell(90, 5, "Cloudrift Infra Solutions Ltd", border=0, ln=True)
    pdf.cell(90, 5, "Suite 7, Tech Tower, Bengaluru 560001", border=0)
    pdf.cell(90, 5, "12, Server Park, Hyderabad 500081", border=0, ln=True)
    pdf.cell(90, 5, "PAN: AABCB5678Z", border=0)
    pdf.cell(90, 5, "GSTIN: 36AABCC9012Z1Z8", border=0, ln=True)
    pdf.ln(6)

    col_w = [15, 75, 20, 25, 25, 30]
    pdf.set_fill_color(30, 80, 180)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(["#", "Item Description", "Qty", "Unit", "Unit Price", "Total (INR)"], col_w):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    items = [
        ("1", "NVIDIA A100 80GB SXM4 GPU (OEM)", "4", "Units", "22,50,000", "90,00,000"),
        ("2", "Dell PowerEdge R750xs Server (32-core)", "2", "Units", "8,40,000", "16,80,000"),
        ("3", "Samsung 3.84TB NVMe SSD (U.2)", "16", "Units", "1,20,000", "19,20,000"),
        ("4", "100GbE InfiniBand Network Switch", "1", "Unit", "5,60,000", "5,60,000"),
        ("5", "APC Smart-UPS 10kVA Rack", "2", "Units", "3,80,000", "7,60,000"),
        ("6", "Rack Mounting & Cabling (Labour)", "1", "Service", "85,000", "85,000"),
        ("7", "3-Year Onsite Hardware Support SLA", "1", "Service", "9,50,000", "9,50,000"),
    ]
    fill = False
    for row in items:
        pdf.set_fill_color(240, 245, 255)
        for val, w in zip(row, col_w):
            pdf.cell(w, 6, val, border=1, fill=fill)
        pdf.ln()
        fill = not fill

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(155, 7, "Sub-Total (before GST):", align="R", border=0)
    pdf.cell(35, 7, "INR 1,49,55,000", border=1, ln=True)
    pdf.cell(155, 7, "GST 18%:", align="R", border=0)
    pdf.cell(35, 7, "INR 26,91,900", border=1, ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(155, 9, "TOTAL ORDER VALUE:", align="R", border=0)
    pdf.cell(35, 9, "INR 1,76,46,900", border=1, ln=True)

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5,
        "Payment Terms: 30% advance on PO confirmation, 70% on delivery and inspection sign-off. "
        "Delivery to: BFAI Data Centre, Plot 22, KIADB Electronics City Phase 2, Bengaluru 560100. "
        "All goods must be accompanied by test certificates and packing lists. "
        "BFAI reserves the right to reject goods that fail incoming quality inspection.")

    pdf.output("sample_documents/purchase_order.pdf")
    print("[OK] purchase_order.pdf")


# ── 4. Product Specification Sheet ───────────────────────────────────────────
def create_product_spec():
    pdf = new_pdf()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "BFAI DocIntel Engine v2.0", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 6, "Product Technical Specification Sheet", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Document ID: BFAI-SPEC-2024-012  |  Rev: 2.0  |  Status: Released", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Product Overview", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "The BFAI DocIntel Engine v2.0 is a cloud-native document intelligence microservice that "
        "provides OCR parsing, LLM-based classification, vector embedding, and agentic retrieval-augmented "
        "generation (RAG) over uploaded documents. It is designed for enterprise document workflows "
        "requiring high accuracy, citation traceability, and sub-2-second query latency at scale.")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Technical Specifications", ln=True)

    specs = [
        ("Supported Input Formats", "PDF (text + scanned), PNG, JPG, JPEG, TIFF, TXT, MD, CSV"),
        ("Max File Size", "20 MB per file; 200 MB per batch request"),
        ("Max Pages per Document", "500 pages"),
        ("OCR Engine", "Tesseract 5.x with LSTM model; fallback to pdfplumber for text-layer PDFs"),
        ("Classification Model", "Groq llama-3.3-70b-versatile; structured JSON output with schema validation"),
        ("Embedding Model", "sentence-transformers/all-MiniLM-L6-v2; 384-dimensional vectors"),
        ("Vector Store", "ChromaDB v0.5.x; cosine similarity; persistent on-disk index"),
        ("RAG Framework", "LangChain v0.2.x; tool-calling agent; top-5 chunk retrieval"),
        ("Chunk Size", "800 tokens; 100-token overlap (RecursiveCharacterTextSplitter)"),
        ("Query Latency (p50)", "< 1.2 seconds (Groq API) + < 50ms ChromaDB retrieval"),
        ("Query Latency (p99)", "< 3.5 seconds under 50 concurrent users"),
        ("TTS Engine", "ElevenLabs eleven_multilingual_v2; streaming audio/mpeg"),
        ("STT Engine", "OpenAI Whisper-1; server-side fallback; 25 MB audio limit"),
        ("Rate Limits", "10 uploads/min; 30 chat queries/min; 20 TTS calls/min per IP"),
        ("Authentication", "API key header (X-API-Key) for production; open for demo deployment"),
        ("Security", "MIME validation, filename sanitisation, UUID-only doc IDs, security headers"),
        ("Deployment", "Docker on Google Cloud Run; asia-south1; auto-scales 0-10 instances"),
        ("Memory Requirement", "2 GiB RAM minimum (for sentence-transformers model loading)"),
        ("API Protocol", "REST/JSON over HTTPS; OpenAPI 3.1 spec at /docs"),
    ]

    col_w = [75, 110]
    pdf.set_fill_color(30, 80, 180)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(["Parameter", "Value"], col_w):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    fill = False
    for param, val in specs:
        pdf.set_fill_color(240, 245, 255)
        pdf.cell(col_w[0], 6, param, border=1, fill=fill)
        pdf.cell(col_w[1], 6, val, border=1, fill=fill)
        pdf.ln()
        fill = not fill

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. API Endpoints", ln=True)
    pdf.set_font("Helvetica", "", 9)
    endpoints = [
        ("POST /api/upload", "Upload 1-10 documents; returns doc_ids; triggers async processing"),
        ("GET  /api/processing-status/{doc_id}", "Poll document processing state"),
        ("GET  /api/documents", "List all indexed documents with metadata"),
        ("GET  /api/documents/{doc_id}", "Get single document detail + classification"),
        ("GET  /api/documents/{doc_id}/page/{n}/image", "Retrieve page PNG thumbnail"),
        ("DELETE /api/documents/{doc_id}", "Remove document from index and storage"),
        ("POST /api/chat", "Send message; returns RAG answer + citations"),
        ("POST /api/voice/speak", "TTS: text -> audio/mpeg stream"),
        ("POST /api/voice/transcribe", "STT: audio file -> transcript text"),
        ("GET  /api/health", "Health check; returns indexed document count"),
    ]
    col_e = [80, 105]
    pdf.set_fill_color(30, 80, 180)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(["Endpoint", "Description"], col_e):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    fill = False
    for ep, desc in endpoints:
        pdf.set_fill_color(240, 245, 255)
        pdf.cell(col_e[0], 6, ep, border=1, fill=fill)
        pdf.cell(col_e[1], 6, desc, border=1, fill=fill)
        pdf.ln()
        fill = not fill

    pdf.output("sample_documents/product_spec.pdf")
    print("[OK] product_spec.pdf")


# ── 5. Non-Disclosure Agreement ───────────────────────────────────────────────
def create_nda():
    pdf = new_pdf()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "MUTUAL NON-DISCLOSURE AGREEMENT", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Strictly Confidential  |  Ref: BFAI-NDA-2024-0042", ln=True, align="C")
    pdf.ln(4)

    nda_sections = [
        ("PARTIES",
         "This Mutual Non-Disclosure Agreement ('Agreement') is entered into on 15 November 2024 between:\n"
         "Disclosing Party 1: BFAI Technologies Pvt Ltd, Suite 7, Tech Tower, Bengaluru 560001 ('BFAI'); and\n"
         "Disclosing Party 2: NovaMed Healthcare Analytics Pvt Ltd, 33 Wellness Hub, Mumbai 400070 ('NovaMed').\n"
         "Both parties may be collectively referred to as 'the Parties' or individually as a 'Party'."),
        ("PURPOSE",
         "The Parties intend to explore a potential business partnership for integrating BFAI's document "
         "intelligence platform with NovaMed's clinical data management system (the 'Proposed Transaction'). "
         "Each Party may disclose Confidential Information solely to evaluate the Proposed Transaction."),
        ("DEFINITION OF CONFIDENTIAL INFORMATION",
         "Confidential Information means any non-public information disclosed by either Party including but "
         "not limited to: technical specifications, source code, ML model architectures, training datasets, "
         "patient data schemas, financial projections, customer lists, pricing strategies, and business plans, "
         "whether disclosed orally, in writing, or in any other medium, and whether or not marked 'confidential'. "
         "Excluded: information that is publicly known, independently developed, or disclosed by a third party lawfully."),
        ("OBLIGATIONS",
         "Each Party agrees to: (a) hold Confidential Information in strict confidence using at least the "
         "same degree of care as it uses for its own confidential information (but not less than reasonable care); "
         "(b) not disclose Confidential Information to any third party without prior written consent; "
         "(c) use Confidential Information solely for evaluating the Proposed Transaction; "
         "(d) limit access to employees and advisors on a strict need-to-know basis who are bound by "
         "confidentiality obligations no less restrictive than those in this Agreement."),
        ("TERM",
         "This Agreement is effective from the date first written above and continues for a period of "
         "3 (three) years, or until the Parties execute a definitive agreement, whichever occurs first. "
         "Obligations of confidentiality survive expiry or termination for a further 5 years with respect "
         "to trade secrets and personal health information."),
        ("RETURN OF INFORMATION",
         "Upon written request, each Party shall promptly return or certifiably destroy all Confidential "
         "Information received, including copies and extracts in any medium, within 10 business days. "
         "One archival copy may be retained by legal counsel solely for compliance purposes."),
        ("REMEDIES",
         "Each Party acknowledges that breach of this Agreement may cause irreparable harm for which "
         "monetary damages may be inadequate. Accordingly, either Party may seek injunctive or equitable "
         "relief in addition to any other remedies available at law."),
        ("GOVERNING LAW",
         "This Agreement shall be governed by the laws of India. Jurisdiction: courts of Bengaluru, Karnataka."),
    ]

    for title, body in nda_sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(3)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 6, "Signed for BFAI Technologies:", border=0)
    pdf.cell(90, 6, "Signed for NovaMed Healthcare Analytics:", border=0, ln=True)
    pdf.ln(10)
    pdf.cell(90, 6, "___________________________", border=0)
    pdf.cell(90, 6, "___________________________", border=0, ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(90, 5, "Rohit Verma, CEO", border=0)
    pdf.cell(90, 5, "Dr. Kavita Menon, COO", border=0, ln=True)
    pdf.cell(90, 5, "Date: 15/11/2024", border=0)
    pdf.cell(90, 5, "Date: 15/11/2024", border=0, ln=True)

    pdf.output("sample_documents/nda_nonamed_bfai.pdf")
    print("[OK] nda_nonamed_bfai.pdf")


if __name__ == "__main__":
    print("Generating additional sample documents...")
    create_employment_contract()
    create_hr_policy()
    create_purchase_order()
    create_product_spec()
    create_nda()
    print("Done. All files in sample_documents/")
