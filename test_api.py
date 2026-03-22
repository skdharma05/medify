"""
Medify API Smoke Tests
Run with: python test_api.py
Requires the server to be running at http://localhost:8000
"""

import sys
import time
import httpx

BASE_URL = "http://localhost:8000"
SAMPLE_RESUME = "tests/sample_resume.txt"
PASS = "✅ PASS"
FAIL = "❌ FAIL"


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))
    return condition


def run_tests() -> None:
    results = []
    session_id = None

    print("\n══════════════════════════════════════")
    print("       Medify API Smoke Tests         ")
    print("══════════════════════════════════════\n")

    with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:

        # ── 1. Health check ──────────────────────────────────────────────
        print("1. Health check")
        r = client.get("/health")
        results.append(check("Status 200", r.status_code == 200, str(r.status_code)))
        results.append(check("api_key_set is True", r.json().get("api_key_set") is True))
        print()

        # ── 2. Upload resume ─────────────────────────────────────────────
        print("2. Upload a valid resume")
        with open(SAMPLE_RESUME, "rb") as f:
            r = client.post("/upload", files={"file": ("sample_resume.txt", f, "text/plain")})
        results.append(check("Status 200", r.status_code == 200, str(r.status_code)))
        if r.status_code == 200:
            session_id = r.json().get("session_id")
            results.append(check("Got session_id", bool(session_id), session_id or "missing"))
        print()

        # ── 3. Query the resume ──────────────────────────────────────────
        if session_id:
            print("3. Query the resume")
            r = client.post("/query", json={"session_id": session_id, "query": "What are this person's technical skills?"})
            results.append(check("Status 200", r.status_code == 200, str(r.status_code)))
            answer = r.json().get("answer", "")
            results.append(check("Non-empty answer", bool(answer.strip()), answer[:80] + "..."))
            print()

        # ── 4. Query on non-existent session ────────────────────────────
        print("4. Query with invalid session_id")
        r = client.post("/query", json={"session_id": "a" * 36, "query": "What skills?"})
        results.append(check("Status 404", r.status_code == 404, str(r.status_code)))
        print()

        # ── 5. Upload invalid file type ──────────────────────────────────
        print("5. Upload invalid file type (.exe)")
        r = client.post("/upload", files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")})
        results.append(check("Status 400", r.status_code == 400, str(r.status_code)))
        print()

        # ── 6. Upload oversized file ─────────────────────────────────────
        print("6. Upload oversized file (> MAX_FILE_SIZE_MB)")
        big_content = b"x" * (6 * 1024 * 1024)  # 6 MB
        r = client.post("/upload", files={"file": ("big.txt", big_content, "text/plain")})
        results.append(check("Status 400", r.status_code == 400, str(r.status_code)))
        print()

        # ── 7. Query string too short ────────────────────────────────────
        print("7. Query string too short (< 3 chars)")
        if session_id:
            r = client.post("/query", json={"session_id": session_id, "query": "Hi"})
            results.append(check("Status 422", r.status_code == 422, str(r.status_code)))
        print()

        # ── 8. Clear session ─────────────────────────────────────────────
        if session_id:
            print("8. Delete session")
            r = client.delete(f"/session/{session_id}")
            results.append(check("Status 200", r.status_code == 200, str(r.status_code)))
            print()

    # ── Summary ──────────────────────────────────────────────────────────
    passed = sum(results)
    total = len(results)
    print("══════════════════════════════════════")
    print(f"  Result: {passed}/{total} checks passed")
    print("══════════════════════════════════════\n")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
