"""
debug_agent.py
Agentic multi-step AI debugger for Game Glitch Investigator.
Pipeline:
  Step 1 — Validate input (guardrail)
  Step 2 — Retrieve relevant KB docs (RAG)
  Step 3 — Analyze code with AI (specialized few-shot prompt)
  Step 4 — Self-check the AI's own diagnosis (reliability)
  Step 5 — Return structured result with confidence score
"""
 
import os
import json
import logging
import anthropic
from rag_retriever import retrieve_and_format
from dotenv import load_dotenv
load_dotenv()
 
# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)
 
# ── Anthropic client ───────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"
 
# ── Few-shot specialization examples (Fine-Tuning / Specialization feature) ────
FEW_SHOT_EXAMPLES = """
=== EXAMPLES OF HOW YOU RESPOND ===
 
Example 1:
User code snippet: `if guess > secret: return 'Too Low'`
Your diagnosis:
{
  "bugs_found": ["Inverted comparison hint: guess > secret should return 'Too High', not 'Too Low'"],
  "severity": "High",
  "fix_suggestion": "Swap the return values: guess > secret → 'Too High', guess < secret → 'Too Low'",
  "snarky_comment": "Classic rookie move — the arrow points the wrong direction, just like your career if you ship this.",
  "confidence": 0.97
}
 
Example 2:
User code snippet: `secret = random.randint(1, 100)` (outside session_state)
Your diagnosis:
{
  "bugs_found": ["State reset bug: secret regenerates on every Streamlit rerun"],
  "severity": "Critical",
  "fix_suggestion": "Wrap in: if 'secret' not in st.session_state: st.session_state.secret = random.randint(1, 100)",
  "snarky_comment": "Your secret number has the memory of a goldfish. It forgets itself every 3 seconds.",
  "confidence": 0.99
}
 
Example 3:
User code snippet: `if attempt_number % 2 == 0: return current_score + 10`
Your diagnosis:
{
  "bugs_found": ["Score rewards wrong guesses on even attempts"],
  "severity": "Medium",
  "fix_suggestion": "Only award points when outcome == 'Win'. Deduct 5 for wrong guesses.",
  "snarky_comment": "Congratulations, you've invented a game where being wrong is profitable. Wall Street called, they're interested.",
  "confidence": 0.95
}
=== END EXAMPLES ===
"""
 
 
# ── Input guardrail ────────────────────────────────────────────────────────────
def validate_input(code_snippet: str) -> tuple[bool, str]:
    """Guardrail: reject empty, too-short, or non-code inputs."""
    if not code_snippet or not code_snippet.strip():
        return False, "⚠️ Input is empty. Please paste some code to analyze."
    if len(code_snippet.strip()) < 10:
        return False, "⚠️ Input too short to be valid code."
    if len(code_snippet) > 8000:
        return False, "⚠️ Input too long (max 8000 chars). Please paste a focused snippet."
    # Rough check: does it look like code?
    code_keywords = ["def ", "if ", "return", "import", "=", "(", ")"]
    if not any(kw in code_snippet for kw in code_keywords):
        return False, "⚠️ This doesn't look like code. Please paste a Python snippet."
    return True, ""
 
 
# ── Step 3: AI diagnosis ───────────────────────────────────────────────────────
def run_diagnosis(code_snippet: str, rag_context: str, step_log: list) -> dict:
    """Call AI with RAG context + few-shot specialization to diagnose bugs."""
    system_prompt = f"""You are GlitchBot — a snarky but brilliant game debugging AI.
You speak like a seasoned game developer who has seen every rookie mistake.
You ALWAYS respond in valid JSON matching this exact schema:
{{
  "bugs_found": ["list of bugs identified"],
  "severity": "Low | Medium | High | Critical",
  "fix_suggestion": "clear fix description",
  "snarky_comment": "one witty, sarcastic observation about the bug",
  "confidence": 0.0 to 1.0
}}
 
{FEW_SHOT_EXAMPLES}
 
Use the retrieved knowledge base entries below to ground your diagnosis.
{rag_context}
"""
 
    user_prompt = f"""Analyze this Python game code for bugs:\n\n```python\n{code_snippet}\n```\n\nRespond ONLY with the JSON object."""
 
    logger.info("Step 3: Sending to AI for diagnosis")
    step_log.append("🤖 Step 3: AI analyzing code with RAG context + few-shot specialization...")
 
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
 
    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
 
    result = json.loads(raw)
    logger.info(f"Step 3 result: {result}")
    return result
 
 
# ── Step 4: Self-check (reliability harness) ──────────────────────────────────
def self_check(diagnosis: dict, code_snippet: str, step_log: list) -> dict:
    """Ask AI to verify its own diagnosis — multi-model agreement pattern."""
    check_prompt = f"""You are a senior code reviewer verifying another AI's bug diagnosis.
 
Original code:
```python
{code_snippet}
```
 
Diagnosis to verify:
{json.dumps(diagnosis, indent=2)}
 
Is this diagnosis accurate? Respond ONLY in JSON:
{{
  "verified": true or false,
  "corrections": "none, or describe what was wrong",
  "final_confidence": 0.0 to 1.0
}}"""
 
    logger.info("Step 4: Running self-check on diagnosis")
    step_log.append("🔍 Step 4: Self-checking diagnosis for accuracy...")
 
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": check_prompt}],
    )
 
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
 
    check_result = json.loads(raw)
    logger.info(f"Step 4 self-check: {check_result}")
    return check_result
 
 
# ── Main agent entrypoint ──────────────────────────────────────────────────────
def run_debug_agent(code_snippet: str) -> dict:
    """
    Full agentic pipeline. Returns a result dict with all steps logged.
    Observable intermediate steps are stored in result['steps'].
    """
    step_log = []
    result = {
        "success": False,
        "steps": step_log,
        "diagnosis": None,
        "self_check": None,
        "error": None,
    }
 
    try:
        # Step 1: Input validation (guardrail)
        step_log.append("🛡️ Step 1: Validating input...")
        valid, err_msg = validate_input(code_snippet)
        if not valid:
            result["error"] = err_msg
            step_log.append(f"❌ Validation failed: {err_msg}")
            logger.warning(f"Input validation failed: {err_msg}")
            return result
        step_log.append("✅ Step 1: Input valid.")
 
        # Step 2: RAG retrieval
        step_log.append("📚 Step 2: Retrieving relevant knowledge base docs...")
        rag_context = retrieve_and_format(code_snippet, top_k=3)
        step_log.append("✅ Step 2: Knowledge base docs retrieved.")
        logger.info("Step 2: RAG context retrieved")
 
        # Step 3: AI diagnosis
        diagnosis = run_diagnosis(code_snippet, rag_context, step_log)
        result["diagnosis"] = diagnosis
        step_log.append(f"✅ Step 3: Diagnosis complete. Severity: {diagnosis.get('severity', 'Unknown')}")
 
        # Step 4: Self-check
        check = self_check(diagnosis, code_snippet, step_log)
        result["self_check"] = check
        final_confidence = check.get("final_confidence", diagnosis.get("confidence", 0.0))
        step_log.append(
            f"✅ Step 4: Self-check {'passed' if check.get('verified') else 'flagged corrections'}. "
            f"Final confidence: {final_confidence:.0%}"
        )
 
        # Step 5: Finalize
        step_log.append("🏁 Step 5: Finalizing result...")
        result["success"] = True
        result["final_confidence"] = final_confidence
        logger.info("Agent pipeline completed successfully")
 
    except json.JSONDecodeError as e:
        err = f"AI returned malformed JSON: {e}"
        result["error"] = err
        step_log.append(f"❌ {err}")
        logger.error(err)
    except Exception as e:
        err = f"Agent error: {str(e)}"
        result["error"] = err
        step_log.append(f"❌ {err}")
        logger.error(err)
 
    return result