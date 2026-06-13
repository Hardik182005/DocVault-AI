"""
stress_test.py - Full BFAI stress test.
1. Upload 100 documents in batches of 10
2. Poll until all indexed
3. Fire 20 concurrent chat queries
4. Test voice TTS endpoint
5. Report latencies and errors
"""
import os, time, glob, asyncio, statistics
import httpx

BASE = os.getenv("BFAI_URL", "https://bfai-hardik-backend-3692981377.asia-south1.run.app")
DOCS_DIR = "stress_docs"
BATCH    = 9   # max 10 per request; use 9 to be safe
TIMEOUT  = 120

CHAT_QUERIES = [
    "What is the total invoice amount due?",
    "Summarise the key findings of the research papers",
    "What medical conditions are mentioned across all documents?",
    "Which documents discuss EBITDA or revenue growth?",
    "What are the termination clauses in the contracts?",
    "List all patient IDs mentioned in medical reports",
    "What machine learning topics are covered in research papers?",
    "Which companies appear most frequently as buyers or sellers?",
    "What security measures are described in any policy documents?",
    "What is the highest contract value mentioned?",
    "Summarise the HR leave policy across all HR documents",
    "What API rate limits are specified in product specs?",
    "Which documents mention GST or tax information?",
    "What are the lab results flagged as HIGH in medical reports?",
    "What datasets are used in the research papers?",
    "Which financial reports show net profit above INR 30 Cr?",
    "What payment terms appear most commonly in invoices?",
    "Describe the arbitration clauses found in contracts",
    "What product categories appear in purchase orders or invoices?",
    "Which documents are classified as strictly confidential?",
]


def batch(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


async def upload_batch(client, files, batch_num):
    t0 = time.time()
    opened = []
    try:
        form = []
        for f in files:
            fh = open(f, "rb")
            opened.append(fh)
            form.append(("files", (os.path.basename(f), fh, "application/octet-stream")))
        resp = await client.post(f"{BASE}/api/upload", files=form, timeout=TIMEOUT)
        elapsed = time.time() - t0
        if resp.status_code == 200:
            data = resp.json()
            doc_ids = [d["doc_id"] for d in data if "doc_id" in d]
            print(f"  [Batch {batch_num:02d}] Uploaded {len(doc_ids)} docs in {elapsed:.1f}s")
            return doc_ids, elapsed
        else:
            print(f"  [Batch {batch_num:02d}] Upload failed: {resp.status_code} - {resp.text[:100]}")
            return [], elapsed
    except Exception as e:
        print(f"  [Batch {batch_num:02d}] Upload error: {e}")
        return [], time.time() - t0
    finally:
        for fh in opened:
            fh.close()


async def poll_all_indexed(client, all_doc_ids, timeout=600):
    """Poll until all docs are indexed or timeout."""
    start = time.time()
    pending = set(all_doc_ids)
    indexed = set()
    errors  = set()

    while pending and (time.time() - start) < timeout:
        done_this_round = set()
        for doc_id in list(pending):
            try:
                r = await client.get(f"{BASE}/api/processing-status/{doc_id}", timeout=30)
                if r.status_code == 200:
                    status = r.json().get("status", "")
                    if status == "indexed":
                        done_this_round.add(doc_id)
                        indexed.add(doc_id)
                    elif status == "error":
                        done_this_round.add(doc_id)
                        errors.add(doc_id)
            except Exception:
                pass
        pending -= done_this_round
        elapsed = time.time() - start
        print(f"  Progress: {len(indexed)} indexed, {len(errors)} errors, {len(pending)} pending ({elapsed:.0f}s)")
        if pending:
            await asyncio.sleep(5)

    return indexed, errors


async def chat_query(client, query, idx):
    t0 = time.time()
    try:
        resp = await client.post(
            f"{BASE}/api/chat",
            json={"message": query, "conversation_history": []},
            timeout=TIMEOUT,
        )
        elapsed = time.time() - t0
        if resp.status_code == 200:
            data = resp.json()
            citations = len(data.get("citations", []))
            answer_len = len(data.get("answer", ""))
            return {"ok": True, "elapsed": elapsed, "citations": citations, "answer_len": answer_len}
        else:
            return {"ok": False, "elapsed": elapsed, "error": resp.status_code}
    except Exception as e:
        return {"ok": False, "elapsed": time.time() - t0, "error": str(e)}


async def test_voice(client):
    t0 = time.time()
    try:
        resp = await client.post(
            f"{BASE}/api/voice/speak",
            json={"text": "BFAI stress test complete. All systems nominal."},
            timeout=30,
        )
        elapsed = time.time() - t0
        return resp.status_code == 200, elapsed, len(resp.content)
    except Exception as e:
        return False, time.time() - t0, 0


async def main():
    print("=" * 60)
    print("BFAI DOCUMENT INTELLIGENCE - STRESS TEST")
    print(f"Backend: {BASE}")
    print("=" * 60)

    # Health check
    async with httpx.AsyncClient() as client:
        try:
            h = await client.get(f"{BASE}/api/health", timeout=15)
            health = h.json()
            print(f"\nHealth: {health}")
        except Exception as e:
            print(f"Backend unreachable: {e}"); return

    all_files = sorted(glob.glob(f"{DOCS_DIR}/*.pdf"))
    print(f"\nFound {len(all_files)} documents in ./{DOCS_DIR}/")

    # â”€â”€ Phase 1: Upload â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print(f"\n{'â”€'*40}")
    print(f"PHASE 1: Uploading {len(all_files)} documents in batches of {BATCH}")
    print(f"{'â”€'*40}")

    all_doc_ids   = []
    upload_times  = []
    upload_errors = 0
    phase1_start  = time.time()

    async with httpx.AsyncClient() as client:
        tasks = [
            upload_batch(client, list(b), i+1)
            for i, b in enumerate(batch(all_files, BATCH))
        ]
        results = await asyncio.gather(*tasks)

    for doc_ids, elapsed in results:
        all_doc_ids.extend(doc_ids)
        upload_times.append(elapsed)
        if not doc_ids:
            upload_errors += 1

    phase1_time = time.time() - phase1_start
    print(f"\nUpload complete: {len(all_doc_ids)} docs submitted in {phase1_time:.1f}s")
    print(f"  Avg batch time : {statistics.mean(upload_times):.2f}s")
    print(f"  Upload errors  : {upload_errors}")

    if not all_doc_ids:
        print("No docs uploaded â€” aborting."); return

    # â”€â”€ Phase 2: Wait for indexing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print(f"\n{'â”€'*40}")
    print(f"PHASE 2: Polling until all {len(all_doc_ids)} docs indexed (max 10 min)")
    print(f"{'â”€'*40}")

    phase2_start = time.time()
    async with httpx.AsyncClient() as client:
        indexed, errors = await poll_all_indexed(client, all_doc_ids)
    phase2_time = time.time() - phase2_start

    print(f"\nIndexing complete in {phase2_time:.1f}s")
    print(f"  Indexed : {len(indexed)}")
    print(f"  Errors  : {len(errors)}")
    print(f"  Avg time/doc: {phase2_time/max(len(all_doc_ids),1):.1f}s")

    # Final health check
    async with httpx.AsyncClient() as client:
        h = await client.get(f"{BASE}/api/health", timeout=15)
        print(f"  Total chunks in ChromaDB: {h.json().get('documents_indexed',0)}")

    # â”€â”€ Phase 3: Concurrent chat â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print(f"\n{'â”€'*40}")
    print(f"PHASE 3: {len(CHAT_QUERIES)} concurrent RAG chat queries")
    print(f"{'â”€'*40}")

    phase3_start = time.time()
    async with httpx.AsyncClient() as client:
        chat_tasks = [chat_query(client, q, i) for i, q in enumerate(CHAT_QUERIES)]
        chat_results = await asyncio.gather(*chat_tasks)
    phase3_time = time.time() - phase3_start

    ok_results = [r for r in chat_results if r["ok"]]
    fail_results = [r for r in chat_results if not r["ok"]]
    latencies = [r["elapsed"] for r in ok_results]
    citations_count = [r["citations"] for r in ok_results]

    print(f"\nChat results ({len(CHAT_QUERIES)} queries fired simultaneously):")
    print(f"  Success rate  : {len(ok_results)}/{len(CHAT_QUERIES)} ({len(ok_results)/len(CHAT_QUERIES)*100:.0f}%)")
    if latencies:
        print(f"  Latency p50   : {statistics.median(latencies):.2f}s")
        print(f"  Latency p95   : {sorted(latencies)[int(len(latencies)*0.95)]:.2f}s")
        print(f"  Latency max   : {max(latencies):.2f}s")
        print(f"  Latency min   : {min(latencies):.2f}s")
        print(f"  Avg citations : {statistics.mean(citations_count):.1f} per answer")
    if fail_results:
        print(f"  Failures      : {[r.get('error') for r in fail_results]}")
    print(f"  Total time    : {phase3_time:.1f}s")

    # Sample answers
    print("\nSample answers:")
    for i, (q, r) in enumerate(zip(CHAT_QUERIES[:3], chat_results[:3])):
        if r["ok"]:
            print(f"\n  Q{i+1}: {q[:60]}...")
            print(f"  Citations: {r['citations']}  |  Answer length: {r['answer_len']} chars  |  {r['elapsed']:.2f}s")

    # â”€â”€ Phase 4: Voice TTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print(f"\n{'â”€'*40}")
    print("PHASE 4: ElevenLabs TTS endpoint test")
    print(f"{'â”€'*40}")

    async with httpx.AsyncClient() as client:
        ok, elapsed, size = await test_voice(client)

    print(f"  Status  : {'OK' if ok else 'FAILED'}")
    print(f"  Latency : {elapsed:.2f}s")
    print(f"  Audio   : {size:,} bytes ({size//1024} KB)")

    # â”€â”€ Summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    total_time = phase1_time + phase2_time + phase3_time
    print(f"\n{'='*60}")
    print("STRESS TEST SUMMARY")
    print(f"{'='*60}")
    print(f"  Documents uploaded  : {len(all_doc_ids)}/100")
    print(f"  Documents indexed   : {len(indexed)}")
    print(f"  Upload time         : {phase1_time:.1f}s")
    print(f"  Index time          : {phase2_time:.1f}s")
    print(f"  Chat queries        : {len(ok_results)}/{len(CHAT_QUERIES)} OK")
    print(f"  Chat p50 latency    : {statistics.median(latencies):.2f}s" if latencies else "  Chat: no results")
    print(f"  Voice TTS           : {'OK' if ok else 'FAILED'} ({elapsed:.2f}s, {size//1024}KB)")
    print(f"  Total test time     : {total_time:.0f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
