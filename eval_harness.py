"""
eval_harness.py
Test Harness / Evaluation Script for Game Glitch Investigator AI Debug Agent.
Runs predefined test cases and prints a pass/fail summary with confidence scores.
 
Usage:
    python eval_harness.py
"""
 
import json
import sys
from debug_agent import run_debug_agent
 
# ── Test Cases ─────────────────────────────────────────────────────────────────
TEST_CASES = [
    {
        "id": "TC001",
        "name": "State Reset Bug",
        "input": "secret = random.randint(1, 100)\n# called on every button click, no session_state",
        "expected_keywords": ["state", "reset", "session"],
        "expected_severity_min": "Medium",
        "should_succeed": True,
    },
    {
        "id": "TC002",
        "name": "Inverted Hints Bug",
        "input": (
            "def check_guess(guess, secret):\n"
            "    if guess > secret:\n"
            "        return 'Too Low'\n"
            "    elif guess < secret:\n"
            "        return 'Too High'\n"
            "    return 'Win'"
        ),
        "expected_keywords": ["inverted", "hint", "high", "low", "comparison"],
        "expected_severity_min": "High",
        "should_succeed": True,
    },
    {
        "id": "TC003",
        "name": "String Comparison Bug",
        "input": (
            "def compare(guess, secret):\n"
            "    if str(guess) > str(secret):\n"
            "        return 'Too High'\n"
            "    return 'Too Low'"
        ),
        "expected_keywords": ["string", "type", "integer", "lexicograph"],
        "expected_severity_min": "Medium",
        "should_succeed": True,
    },
    {
        "id": "TC004",
        "name": "Score Rewarding Wrong Guesses",
        "input": (
            "def update_score(score, attempt_number):\n"
            "    if attempt_number % 2 == 0:\n"
            "        return score + 10\n"
            "    return score"
        ),
        "expected_keywords": ["score", "wrong", "reward", "even", "attempt"],
        "expected_severity_min": "Medium",
        "should_succeed": True,
    },
    {
        "id": "TC005",
        "name": "Clean Code (No Bugs)",
        "input": (
            "def check_guess(guess: int, secret: int):\n"
            "    guess = int(guess)\n"
            "    secret = int(secret)\n"
            "    if guess == secret:\n"
            "        return 'Win', 'Correct!'\n"
            "    elif guess > secret:\n"
            "        return 'Too High', 'Go LOWER!'\n"
            "    else:\n"
            "        return 'Too Low', 'Go HIGHER!'"
        ),
        "expected_keywords": [],
        "expected_severity_min": None,
        "should_succeed": True,
    },
    {
        "id": "TC006",
        "name": "Empty Input Guardrail",
        "input": "",
        "expected_keywords": [],
        "expected_severity_min": None,
        "should_succeed": False,  # Should fail validation
    },
    {
        "id": "TC007",
        "name": "Non-Code Input Guardrail",
        "input": "hello world this is not code at all",
        "expected_keywords": [],
        "expected_severity_min": None,
        "should_succeed": False,  # Should fail guardrail
    },
    {
        "id": "TC008",
        "name": "Difficulty Range Inconsistency",
        "input": (
            "# In function:\n"
            "def get_range(difficulty):\n"
            "    if difficulty == 'Hard': return 1, 50\n\n"
            "# In New Game button:\n"
            "secret = random.randint(1, 100)  # Hard mode but using 1-100"
        ),
        "expected_keywords": ["range", "difficulty", "inconsistency", "hard"],
        "expected_severity_min": "Medium",
        "should_succeed": True,
    },
]
 
SEVERITY_ORDER = ["Low", "Medium", "High", "Critical"]
 
 
def severity_gte(actual: str, minimum: str) -> bool:
    """Return True if actual severity >= minimum severity."""
    if minimum is None:
        return True
    try:
        return SEVERITY_ORDER.index(actual) >= SEVERITY_ORDER.index(minimum)
    except ValueError:
        return False
 
 
def keywords_found(text: str, keywords: list[str]) -> list[str]:
    """Return which keywords appear in text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]
 
 
def run_eval():
    """Run all test cases and print a summary."""
    print("=" * 65)
    print("  GAME GLITCH INVESTIGATOR — AI DEBUG AGENT EVALUATION HARNESS")
    print("=" * 65)
    print(f"  Running {len(TEST_CASES)} test cases...\n")
 
    results = []
    total_confidence = 0.0
    confidence_count = 0
 
    for tc in TEST_CASES:
        print(f"[{tc['id']}] {tc['name']}")
        print(f"  Input: {tc['input'][:60].strip()}{'...' if len(tc['input']) > 60 else ''}")
 
        agent_result = run_debug_agent(tc["input"])
        passed = True
        notes = []
 
        if tc["should_succeed"]:
            # Expect agent to succeed
            if not agent_result["success"]:
                passed = False
                notes.append(f"Agent failed unexpectedly: {agent_result.get('error')}")
            else:
                diagnosis = agent_result.get("diagnosis", {})
                diag_text = json.dumps(diagnosis).lower()
                confidence = agent_result.get("final_confidence", 0)
                total_confidence += confidence
                confidence_count += 1
 
                # Check expected keywords in diagnosis
                if tc["expected_keywords"]:
                    found = keywords_found(diag_text, tc["expected_keywords"])
                    missing = [kw for kw in tc["expected_keywords"] if kw not in found]
                    if len(found) == 0:
                        passed = False
                        notes.append(f"No expected keywords found. Missing: {tc['expected_keywords']}")
                    elif missing:
                        notes.append(f"Partial keyword match. Missing: {missing}")
 
                # Check minimum severity
                actual_severity = diagnosis.get("severity", "Low")
                if tc["expected_severity_min"]:
                    if not severity_gte(actual_severity, tc["expected_severity_min"]):
                        passed = False
                        notes.append(
                            f"Severity too low: got '{actual_severity}', "
                            f"expected >= '{tc['expected_severity_min']}'"
                        )
 
                notes.append(f"Confidence: {confidence:.0%}")
                notes.append(f"Severity: {actual_severity}")
                notes.append(f"Bugs found: {diagnosis.get('bugs_found', [])}")
        else:
            # Expect agent to fail (guardrail triggered)
            if agent_result["success"]:
                passed = False
                notes.append("Expected guardrail to block this input, but agent succeeded.")
            else:
                notes.append(f"Guardrail correctly rejected: {agent_result.get('error')}")
 
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  Result: {status}")
        for note in notes:
            print(f"    → {note}")
        print()
 
        results.append({"id": tc["id"], "name": tc["name"], "passed": passed})
 
    # Summary
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count
    avg_confidence = (total_confidence / confidence_count) if confidence_count > 0 else 0
 
    print("=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print(f"  Total Tests : {len(results)}")
    print(f"  Passed      : {passed_count} ✅")
    print(f"  Failed      : {failed_count} ❌")
    print(f"  Pass Rate   : {passed_count / len(results):.0%}")
    print(f"  Avg Confidence (successful runs): {avg_confidence:.0%}")
    print()
 
    if failed_count > 0:
        print("  Failed Tests:")
        for r in results:
            if not r["passed"]:
                print(f"    - [{r['id']}] {r['name']}")
    print("=" * 65)
 
    return passed_count, len(results)
 
 
if __name__ == "__main__":
    passed, total = run_eval()
    sys.exit(0 if passed == total else 1)
 