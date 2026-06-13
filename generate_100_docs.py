"""
generate_100_docs.py - Generates 100 varied synthetic documents for stress testing.
Categories: invoices(20), research(20), medical(15), financial(15), contracts(10), HR(10), product-spec(10)
Usage: python generate_100_docs.py
"""
import os, random
from fpdf import FPDF

OUT = "stress_docs"
os.makedirs(OUT, exist_ok=True)

def pdf():
    p = FPDF()
    p.set_auto_page_break(auto=True, margin=15)
    return p

def h(p, txt, size=14, style="B"):
    p.set_font("Helvetica", style, size)
    p.multi_cell(0, 8, txt)
    p.ln(2)

def body(p, txt, size=10):
    p.set_font("Helvetica", "", size)
    p.multi_cell(0, 6, txt)
    p.ln(2)

def table(p, headers, rows, col_w=None):
    if col_w is None:
        col_w = [int(190 / len(headers))] * len(headers)
    p.set_font("Helvetica", "B", 9)
    p.set_fill_color(60, 80, 180)
    p.set_text_color(255, 255, 255)
    for h_txt, w in zip(headers, col_w):
        p.cell(w, 7, h_txt, border=1, fill=True)
    p.ln()
    p.set_text_color(0, 0, 0)
    p.set_font("Helvetica", "", 9)
    for i, row in enumerate(rows):
        p.set_fill_color(245, 247, 255) if i % 2 == 0 else p.set_fill_color(255,255,255)
        for val, w in zip(row, col_w):
            p.cell(w, 6, str(val), border=1, fill=True)
        p.ln()

COMPANIES = ["Nexus Tech","AquaCore Ltd","PrimeLead Pvt","BridgeWave","ClearPath Inc",
             "DataSync","EagleSoft","FocusAI","GreenPulse","HarbourNet",
             "IndigoLabs","JetStream","KaleidoSys","LunaTech","MorningBell"]
PRODUCTS  = ["AI Consulting","Cloud Storage","OCR Suite","RAG Engine","Data Pipeline",
             "Vision API","NLP Package","Workflow Bot","Security Audit","DevOps Pack"]
PEOPLE    = ["Arjun Sharma","Priya Nair","Rohit Verma","Ananya Singh","Kavita Mehta",
             "Suresh Pillai","Deepa Rajan","Vikram Bose","Neha Joshi","Raj Kapoor"]
CITIES    = ["Bengaluru","Mumbai","Pune","Hyderabad","Chennai","Delhi","Kolkata","Ahmedabad"]
TOPICS    = ["Transformer Architectures","Federated Learning","Graph Neural Networks",
             "Reinforcement Learning","Diffusion Models","Multimodal LLMs","RAG Systems",
             "Efficient Fine-Tuning","Neural Architecture Search","Knowledge Distillation",
             "Attention Mechanisms","Zero-Shot Generalization","Self-Supervised Learning",
             "Continual Learning","Causal Inference in ML","Vision-Language Models",
             "LLM Alignment","Robustness to Distribution Shift","Explainable AI","AI Safety"]
DISEASES  = ["Type 2 Diabetes","Hypertension","Anaemia","Dyslipidaemia","Hypothyroidism",
             "Chronic Kidney Disease","Asthma","GERD","Vitamin D Deficiency","Anxiety Disorder"]
DEPTS     = ["Engineering","Marketing","Finance","Operations","Legal","HR","Product","Sales"]


# ── 1. Invoices (20) ──────────────────────────────────────────────────────────
def make_invoice(n):
    p = pdf(); p.add_page()
    buyer  = random.choice(COMPANIES)
    seller = random.choice([c for c in COMPANIES if c != buyer])
    inv_no = f"INV-2025-{1000+n:04d}"
    date   = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    items  = random.sample(PRODUCTS, random.randint(2,5))
    rows, sub = [], 0
    for itm in items:
        qty   = random.randint(1,10)
        price = random.randint(10000,200000)
        gst   = int(price * qty * 0.18)
        total = price * qty + gst
        sub  += total
        rows.append((itm, qty, f"INR {price:,}", f"INR {gst:,}", f"INR {total:,}"))

    h(p, "INVOICE", 18)
    body(p, f"Invoice No: {inv_no}   Date: {date}   Due: Net-30")
    body(p, f"From: {seller}, {random.choice(CITIES)}")
    body(p, f"To:   {buyer}, {random.choice(CITIES)}")
    p.ln(3)
    table(p, ["Description","Qty","Unit Price","GST 18%","Total INR"],
          rows, [65,15,35,30,40])
    p.ln(4)
    p.set_font("Helvetica","B",11)
    p.cell(145,8,"TOTAL AMOUNT DUE:", align="R", border=0)
    p.cell(40,8,f"INR {sub:,}", border=1, ln=True)
    body(p, f"Bank: HDFC Bank  A/C: {random.randint(10000000000,99999999999)}  IFSC: HDFC000{random.randint(1000,9999)}")
    p.output(f"{OUT}/invoice_{n:03d}.pdf")


# ── 2. Research papers (20) ───────────────────────────────────────────────────
def make_research(n):
    p = pdf()
    topic = TOPICS[n % len(TOPICS)]
    authors = random.sample(PEOPLE, 3)

    p.add_page()
    h(p, f"{topic}: A Comprehensive Study", 15)
    body(p, f"Authors: {', '.join(authors)} - BFAI Research Lab")
    body(p, f"arXiv:2025.{10000+n:05d}  |  Submitted to NeurIPS 2025")
    p.ln(2)
    h(p, "Abstract", 12)
    body(p, (
        f"We present a novel approach to {topic.lower()} that achieves state-of-the-art results "
        f"on standard benchmarks. Our method introduces a new training objective that improves "
        f"convergence by {random.randint(15,45)}% while reducing computational cost by "
        f"{random.randint(20,60)}%. Experiments on {random.randint(3,8)} datasets confirm "
        f"consistent improvements over strong baselines. Code will be released at github.com/bfai-research/{topic.lower().replace(' ','-')}."
    ))

    sections = [
        ("1. Introduction",
         f"The field of {topic.lower()} has seen rapid progress in recent years. "
         f"However, key challenges remain around scalability, generalization, and computational efficiency. "
         f"This work addresses these gaps through a principled framework that builds on prior work "
         f"while introducing key innovations in the training procedure and model architecture."),
        ("2. Related Work",
         f"Seminal work by Vaswani et al. (2017) laid the foundation for modern {topic.lower()} research. "
         f"Subsequent contributions from Brown et al. (2020), Wei et al. (2022), and Ouyang et al. (2022) "
         f"demonstrated the power of scale and instruction tuning. Our work differentiates by focusing on "
         f"sample efficiency and robustness, areas less explored in the prior literature."),
        ("3. Methodology",
         f"We propose a {random.randint(6,24)}-layer architecture with {random.randint(128,1024)} hidden dimensions. "
         f"Training uses a batch size of {random.choice([512,1024,2048,4096])} tokens with a cosine "
         f"learning rate schedule over {random.randint(50,200)}k steps. The key innovation is a "
         f"modified attention kernel that reduces the quadratic complexity to O(n log n)."),
        ("4. Experiments",
         f"We evaluate on {random.randint(3,6)} benchmarks achieving {random.uniform(70,95):.1f}% accuracy "
         f"on the primary task. Ablations confirm each component contributes positively. "
         f"Inference throughput is {random.randint(2,8)}x faster than the baseline."),
        ("5. Conclusion",
         f"We presented a new approach to {topic.lower()} that advances the state of the art while "
         f"improving efficiency. Future work will explore scaling to larger models and extending "
         f"to multilingual and multimodal settings."),
    ]
    for title, text in sections:
        p.add_page()
        h(p, title, 12)
        body(p, text)
    p.output(f"{OUT}/research_{n:03d}.pdf")


# ── 3. Medical reports (15) ───────────────────────────────────────────────────
def make_medical(n):
    p = pdf(); p.add_page()
    patient  = random.choice(PEOPLE)
    pid      = f"PT-2025-{10000+n:05d}"
    disease  = DISEASES[n % len(DISEASES)]
    doctor   = random.choice([x for x in PEOPLE if x != patient])
    hospital = f"{random.choice(['Sunrise','Apollo','Fortis','Max','AIIMS'])} Hospital, {random.choice(CITIES)}"

    h(p, "PATIENT MEDICAL REPORT", 14)
    body(p, "STRICTLY CONFIDENTIAL - For Authorised Medical Personnel Only")
    p.ln(2)
    h(p, "Patient Details", 11)
    for lbl, val in [("Patient Name",patient),("Patient ID",pid),
                     ("Diagnosis",disease),("Doctor",doctor),("Hospital",hospital),
                     ("Date",f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}")]:
        p.set_font("Helvetica","B",10); p.cell(55,6,f"{lbl}:",border=0)
        p.set_font("Helvetica","",10); p.cell(0,6,val,border=0,ln=True)

    p.ln(3)
    h(p, "Lab Results", 11)
    hb_val = round(random.uniform(9,16),1)
    bp_sys = random.randint(100,160); bp_dia = random.randint(60,100)
    glucose = random.randint(80,220)
    table(p, ["Parameter","Result","Unit","Reference","Flag"],
          [("Haemoglobin", hb_val, "g/dL", "12-16", "LOW" if hb_val<12 else "Normal"),
           ("Blood Pressure", f"{bp_sys}/{bp_dia}", "mmHg", "120/80", "HIGH" if bp_sys>130 else "Normal"),
           ("Fasting Glucose", glucose, "mg/dL", "70-100", "HIGH" if glucose>100 else "Normal"),
           ("Creatinine", round(random.uniform(0.6,2.5),2), "mg/dL", "0.6-1.2",
            "HIGH" if random.random()>0.5 else "Normal")],
          [50,35,25,40,30])
    p.ln(3)
    h(p, "Assessment & Treatment Plan", 11)
    body(p, (
        f"Patient presents with {disease}. Current lab values indicate "
        f"{'controlled' if random.random()>0.5 else 'uncontrolled'} disease state. "
        f"Plan: {'Continue current medication regimen' if random.random()>0.5 else 'Adjust dosage per new results'}. "
        f"Lifestyle modifications advised. Follow-up in {random.randint(4,12)} weeks."
    ))
    body(p, f"Prescribed: {random.choice(['Metformin 500mg BD','Amlodipine 5mg OD','Levothyroxine 50mcg OD','Atorvastatin 10mg OD','Pantoprazole 40mg OD'])}")
    p.output(f"{OUT}/medical_{n:03d}.pdf")


# ── 4. Financial reports (15) ─────────────────────────────────────────────────
def make_financial(n):
    p = pdf()
    company = random.choice(COMPANIES)
    quarter = f"Q{(n%4)+1} FY{2023 + n//4}"
    revenue = random.randint(50,500)
    profit  = int(revenue * random.uniform(0.1, 0.3))
    ebitda  = int(revenue * random.uniform(0.15, 0.35))

    p.add_page()
    h(p, f"{company} - {quarter} Financial Report", 14)
    body(p, "INTERNAL DISTRIBUTION ONLY")
    p.ln(2)
    h(p, "Executive Summary", 11)
    body(p, (
        f"{company} delivered {quarter} revenue of INR {revenue} Cr, "
        f"representing a {random.randint(5,35)}% YoY {'increase' if random.random()>0.3 else 'decline'}. "
        f"EBITDA margin stood at {int(ebitda/revenue*100)}%. "
        f"Net profit reached INR {profit} Cr. "
        f"Customer base grew to {random.randint(500,5000):,} active subscribers."
    ))
    p.ln(2)
    h(p, "P&L Summary (INR Crore)", 11)
    prev = int(revenue * random.uniform(0.8,1.1))
    table(p, ["Metric","Current","Previous","Change"],
          [("Revenue", revenue, prev, f"{int((revenue-prev)/prev*100):+}%"),
           ("Gross Profit", int(revenue*0.6), int(prev*0.58), "+3pp"),
           ("EBITDA", ebitda, int(prev*0.22), f"{int((ebitda-prev*0.22)/(prev*0.22)*100):+}%"),
           ("Net Profit", profit, int(prev*0.15), f"{int((profit-prev*0.15)/(prev*0.15)*100):+}%"),
           ("EPS (INR)", round(profit/random.randint(10,50),2), round(prev*0.15/random.randint(10,50),2), "+")],
          [65,35,35,45])
    p.add_page()
    h(p, "Segment Breakdown", 11)
    segs = random.sample(["SaaS","Professional Services","Data Products","Hardware","Licensing","Support"], 3)
    seg_rows = [(s, random.randint(5,int(revenue*0.6)), f"{random.randint(5,40)}%") for s in segs]
    table(p, ["Segment","Revenue (Cr)","Growth"], seg_rows, [80,55,50])
    p.ln(4)
    h(p, "Guidance", 11)
    body(p, f"Full-year FY2025 revenue guidance: INR {int(revenue*3.8)}-{int(revenue*4.2)} Cr. "
            f"The board recommends a dividend of INR {random.randint(1,10)}.{random.randint(0,9)}0 per share.")
    p.output(f"{OUT}/financial_{n:03d}.pdf")


# ── 5. Contracts (10) ─────────────────────────────────────────────────────────
def make_contract(n):
    p = pdf(); p.add_page()
    party_a = random.choice(COMPANIES)
    party_b = random.choice([c for c in COMPANIES if c != party_a])
    contract_types = ["Service Agreement","Software License","Consulting Agreement",
                      "Partnership MOU","Vendor Contract","SaaS Subscription Agreement",
                      "Data Processing Agreement","Maintenance Contract","Outsourcing Agreement","Framework Agreement"]
    ctype = contract_types[n % len(contract_types)]
    value = random.randint(5,200)
    duration = random.randint(1,36)

    h(p, ctype.upper(), 15)
    body(p, f"Contract Ref: BFAI-CTR-2025-{100+n:04d}   Date: 2025-{random.randint(1,12):02d}-01")
    p.ln(2)
    for title, text in [
        ("PARTIES", f"Party A: {party_a}, {random.choice(CITIES)}.\nParty B: {party_b}, {random.choice(CITIES)}."),
        ("SCOPE OF WORK", f"Party A agrees to provide {random.choice(PRODUCTS)} services to Party B. "
            f"The engagement covers {random.choice(DEPTS)} department requirements for a period of {duration} months. "
            f"Deliverables include: documentation, training, integration support, and SLA-backed uptime guarantee."),
        ("CONTRACT VALUE", f"Total contract value: INR {value} Lakhs, payable as follows: "
            f"40% upfront on signing, 30% at midpoint milestone, 30% on final delivery and sign-off. "
            f"Late payment penalty: 2% per month on outstanding amount."),
        ("WARRANTIES", f"Party A warrants that services will be delivered by qualified professionals "
            f"and meet the agreed quality standards. Party B warrants timely provision of access, data, and feedback."),
        ("TERMINATION", f"Either party may terminate with {random.randint(30,90)} days written notice. "
            f"Immediate termination for material breach. IP and data revert to Party B on termination."),
        ("GOVERNING LAW", f"This agreement is governed by Indian law. Disputes resolved by arbitration in {random.choice(CITIES)}."),
    ]:
        h(p, title, 11)
        body(p, text)
    p.output(f"{OUT}/contract_{n:03d}.pdf")


# ── 6. HR Policy docs (10) ───────────────────────────────────────────────────
def make_hr(n):
    p = pdf(); p.add_page()
    dept = DEPTS[n % len(DEPTS)]
    policies = ["Recruitment Policy","Performance Management Policy","Leave & Attendance Policy",
                "Code of Conduct","Expense Reimbursement Policy","Training & Development Policy",
                "Remote Work Policy","Grievance Redressal Policy","Diversity & Inclusion Policy","Exit Policy"]
    pol_name = policies[n % len(policies)]

    h(p, f"BFAI Technologies - {pol_name}", 14)
    body(p, f"Version: {random.randint(1,5)}.{random.randint(0,9)}  Effective: 2025-01-01  Department: {dept}")
    p.ln(2)
    for i in range(1, random.randint(5,8)):
        h(p, f"{i}. Section {i}", 11)
        body(p, (
            f"This section outlines the policy for {dept} employees regarding "
            f"{pol_name.lower()} procedures. All staff must adhere to these guidelines. "
            f"Non-compliance may result in disciplinary action. "
            f"Exceptions require approval from the department head and HR Business Partner. "
            f"Review cycle: annual, or sooner if regulatory requirements change. "
            f"Contact: hr-policy@bfai.in for queries."
        ))
    p.output(f"{OUT}/hr_{n:03d}.pdf")


# ── 7. Product specs (10) ─────────────────────────────────────────────────────
def make_spec(n):
    p = pdf(); p.add_page()
    product = random.choice(PRODUCTS)
    version = f"{random.randint(1,5)}.{random.randint(0,9)}"
    h(p, f"{product} - Technical Specification v{version}", 14)
    body(p, f"Doc ID: BFAI-SPEC-2025-{200+n:04d}  Status: Released  Classification: Internal")
    p.ln(2)
    h(p, "Product Overview", 11)
    body(p, f"The {product} is a cloud-native microservice providing enterprise-grade capabilities. "
            f"Designed for high availability, it supports {random.randint(100,10000):,} concurrent users "
            f"with {random.uniform(99.5,99.99):.2f}% SLA uptime guarantee.")
    p.ln(2)
    h(p, "Technical Specifications", 11)
    specs = [
        ("Supported Protocols", "REST/JSON, gRPC, WebSocket"),
        ("Authentication", "OAuth 2.0 / API Key / SAML 2.0"),
        ("Rate Limits", f"{random.randint(100,10000)} req/min per tenant"),
        ("Data Retention", f"{random.randint(30,365)} days (configurable)"),
        ("Encryption", "AES-256 at rest, TLS 1.3 in transit"),
        ("Max Payload", f"{random.randint(1,100)} MB"),
        ("P99 Latency", f"< {random.randint(50,500)} ms"),
        ("Deployment", "Docker / Kubernetes / Cloud Run"),
        ("Region", f"{random.choice(['asia-south1','us-central1','europe-west1'])}"),
        ("Scaling", f"Auto-scale 0 to {random.randint(10,100)} instances"),
    ]
    table(p, ["Parameter","Value"], specs, [80,105])
    p.ln(3)
    h(p, "API Reference", 11)
    body(p, f"Base URL: https://api.bfai.in/{product.lower().replace(' ','-')}/v{version.split('.')[0]}\n"
            f"Auth header: X-API-Key: <your_key>\n"
            f"Full OpenAPI spec at: /docs\nWebhook support: yes (configurable endpoint)")
    p.output(f"{OUT}/spec_{n:03d}.pdf")


# ── Generate all 100 docs ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating 100 synthetic documents...")
    counts = {"invoice":0,"research":0,"medical":0,"financial":0,"contract":0,"hr":0,"spec":0}

    for i in range(20):
        make_invoice(i+1);   counts["invoice"]+=1
        make_research(i+1);  counts["research"]+=1
    for i in range(15):
        make_medical(i+1);   counts["medical"]+=1
        make_financial(i+1); counts["financial"]+=1
    for i in range(10):
        make_contract(i+1);  counts["contract"]+=1
        make_hr(i+1);        counts["hr"]+=1
        make_spec(i+1);      counts["spec"]+=1

    total = sum(counts.values())
    print(f"Done! {total} files written to ./{OUT}/")
    for k,v in counts.items(): print(f"  {k}: {v}")
