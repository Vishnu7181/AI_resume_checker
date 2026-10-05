import json
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
API_BASE = os.getenv(
    "AI_API_BASE",
    "https://api.openai-compatible.com/v1"
)
AI_MODEL = os.getenv("AI_MODEL")


SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) resume analyst.

Compare the RESUME with the JOB DESCRIPTION and respond ONLY with valid JSON,
no markdown, no extra text, in exactly this schema:

{
  "score": <int 0-100 match percentage>,
  "ats_score": <int 0-100 ATS parse-compatibility>,
  "matched_keywords": ["strings present in both resume and JD"],
  "missing_keywords": ["strings in JD but absent from resume"],
  "suggestions": [
    {
      "severity": "critical"|"warning"|"tip",
      "title": "short title",
      "detail": "actionable advice"
    }
  ]
}

Rules:
- 5 suggestions, ordered critical → tip.
- Keywords must be concrete (skills, tools, qualifications), max 20 each.
- Score must reflect keyword overlap + seniority/qualification fit.
"""


ANALYSIS_PROMPT = """Compare this resume with the job description.

Return:
- match score (%)
- matched keywords
- missing keywords
- missing skills
- 5 improvement suggestions

Return everything in JSON format.

=== JOB DESCRIPTION ===
{jd}

=== RESUME ===
{resume}
"""

async def analyze_resume(resume_text: str, job_description: str) -> dict:
    try:
        raw = await _call_ai(resume_text, job_description)
        return _parse_and_validate(raw, resume_text, job_description)
    except Exception as e:
        print(f"[analyzer] AI call failed: {e}")   # shows in terminal
        return _fallback_analysis(resume_text, job_description)



import certifi   # add at top with other imports


async def _call_ai(resume_text: str, job_description: str) -> str:
    if not API_KEY:
        raise RuntimeError("AI_API_KEY not set in .env")

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ANALYSIS_PROMPT.format(
                    jd=job_description[:8000],
                    resume=resume_text[:8000]
                )
            }
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    import asyncio

    async with httpx.AsyncClient(timeout=60, verify=certifi.where()) as client:
        for attempt in range(3):
            resp = await client.post(
                f"{API_BASE}/chat/completions",
                headers=headers,
                json=payload
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]

            print(f"[analyzer] Attempt {attempt+1} failed: {resp.status_code} {resp.text[:200]}")
            if resp.status_code >= 500:
                await asyncio.sleep(2 * (attempt + 1))   # 2s, 4s, 6s
                continue
            resp.raise_for_status()   # 4xx errors: fail immediately

        resp.raise_for_status()



def _parse_and_validate(
    raw: str,
    resume_text: str,
    jd: str
) -> dict:

    data = _safe_json(raw)

    if data is None:
        return _fallback_analysis(resume_text, jd)

    score = data.get("score", 0)

    return {
        "score": _clamp(score, 0, 100),

        "ats_score": _clamp(
            data.get(
                "ats_score",
                _clamp(score, 0, 100) + 10
            ),
            0,
            100
        ),

        "matched_keywords": _clean_list(
            data.get("matched_keywords")
        ),

        "missing_keywords": _clean_list(
            data.get("missing_keywords")
        ),

        "suggestions": _clean_suggestions(
            data.get("suggestions")
        ),
    }


def _safe_json(raw: str) -> dict | None:
    """Handle models that wrap JSON in markdown fences or add prose."""

    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        raw = raw.removeprefix("json").strip()

    try:
        return json.loads(raw)

    except json.JSONDecodeError:

        start = raw.find("{")
        end = raw.rfind("}")

        if start != -1 and end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                return None

    return None


def _clean_list(items, limit=20):
    return [
        str(i).strip()
        for i in (items or [])
        if str(i).strip()
    ][:limit]


def _clamp(v, lo=0, hi=100):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return 0


def _clean_suggestions(items):
    out = []

    for s in (items or [])[:5]:

        if isinstance(s, str):
            s = {
                "severity": "tip",
                "title": s[:60],
                "detail": s
            }

        out.append({
            "severity": (
                s.get("severity", "tip")
                if s.get("severity") in (
                    "critical",
                    "warning",
                    "tip"
                )
                else "tip"
            ),

            "title": str(
                s.get("title", "Suggestion")
            )[:100],

            "detail": str(
                s.get("detail", "")
            ),
        })

    return out


def _fallback_analysis(
    resume_text: str,
    jd: str
) -> dict:

    STOP = {
        "the", "a", "an", "and", "or", "in",
        "on", "for", "to", "of", "with", "is",
        "are", "at", "by", "be", "as", "you",
        "your", "our", "we", "will", "have",
        "this", "that"
    }

    def words(text):
        return {
            w.strip(".,;:()")
            for w in text.lower().split()
            if len(w) > 2
            and w.strip(".,;:()") not in STOP
        }

    jd_w = words(jd)
    res_w = words(resume_text)

    matched = sorted(jd_w & res_w)
    missing = sorted(jd_w - res_w)

    score = round(
        100 * len(matched) / max(len(jd_w), 1)
    )

    return {
        "score": score,

        "ats_score": min(
            98,
            score + 10
        ),

        "matched_keywords": matched[:20],

        "missing_keywords": missing[:20],

        "suggestions": [
            {
                "severity": "warning",
                "title": "Fallback analysis used",
                "detail": (
                    "AI analysis was unavailable; "
                    "this score is based on simple "
                    "keyword overlap. Try again shortly."
                ),
            }
        ],
    }