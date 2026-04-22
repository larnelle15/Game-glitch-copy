# 🎮 Game Glitch Investigator: AI Debug Agent

> **Applied AI System — Module 4 Final Project**
> Extended from: `ai110-module1show-gameglitchinvestigator-starter`

---

## 📌 Base Project

**Original Project:** Game Glitch Investigator (Module 1)

The original project was a broken Streamlit number-guessing game where students had to find and fix three intentional bugs: a Streamlit session state reset bug causing the secret number to regenerate on every button click, inverted Higher/Lower hints that actively misled the player, and a score function that rewarded wrong guesses on even-numbered attempts. After fixing the bugs, students refactored logic into `logic_utils.py` and verified correctness with pytest.

---

## 🚀 What's New in This Version

This project extends the base game into a full **Applied AI System** with four major AI features:

| Feature | Description |
|---|---|
| **RAG Enhancement** | A custom Glitch Knowledge Base (6 bug pattern docs) is searched before every AI diagnosis. The AI's answer is grounded in retrieved context, not just its training data. |
| **Agentic Workflow** | A 5-step debug agent pipeline: input validation → RAG retrieval → AI diagnosis → self-check → structured result. Each step is observable in the UI. |
| **Specialization** | GlitchBot responds with a consistent snarky game-dev persona using 3 few-shot examples injected into every prompt. Output measurably differs from a generic baseline. |
| **Test Harness** | `eval_harness.py` runs 8 predefined test cases, checks keyword coverage, severity levels, and guardrail behavior, then prints a pass/fail summary with confidence scores. |

---

## 🏗️ Architecture Overview

<img width="2416" height="4840" alt="Code Snippet Input-2026-04-20-035454" src="https://github.com/user-attachments/assets/2327c40b-3587-465a-b122-30d952f92e5c" />


---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```
On Windows:
```bash
set ANTHROPIC_API_KEY=your_key_here
```

### 4. Run the app
```bash
python -m streamlit run app.py
```

### 5. Run unit tests
```bash
pytest tests/ -v
```

### 6. Run the evaluation harness
```bash
python eval_harness.py
```

---

## 🖥️ Sample Interactions

### Example 1 — State Reset Bug
**Input:**
```python
secret = random.randint(1, 100)
# called on every button click
```
**AI Output:**
```json
{
  "bugs_found": ["State reset bug: secret regenerates on every Streamlit rerun"],
  "severity": "Critical",
  "fix_suggestion": "Wrap in: if 'secret' not in st.session_state: ...",
  "snarky_comment": "Your secret number has the memory of a goldfish. It forgets itself every 3 seconds.",
  "confidence": 0.99
}
```
Self-check: ✅ Verified | Confidence: 99%

---

### Example 2 — Inverted Hints
**Input:**
```python
if guess > secret:
    return 'Too Low'
elif guess < secret:
    return 'Too High'
```
**AI Output:**
```json
{
  "bugs_found": ["Inverted comparison: guess > secret returns 'Too Low' instead of 'Too High'"],
  "severity": "High",
  "fix_suggestion": "Swap: guess > secret → 'Too High', guess < secret → 'Too Low'",
  "snarky_comment": "Classic rookie move — the arrow points the wrong direction, just like your career if you ship this.",
  "confidence": 0.97
}
```

---

### Example 3 — Guardrail (Empty Input)
**Input:** *(empty)*
**Agent Response:** `⚠️ Input is empty. Please paste some code to analyze.`
Agent pipeline halts at Step 1. No AI call made.

---

## 🔧 Eval Harness Summary (Sample Run)
Total Tests : 8
Passed      : 7 ✅
Failed      : 1 ❌
Pass Rate   : 88%
Avg Confidence: 94%
Note: TC005 (clean code) may flag low-severity issues —
the AI finds something to comment on in even correct code.

---

## 🎨 Design Decisions

**Why keyword-based RAG instead of embeddings?** For 6 documents, a simple keyword scorer is faster, requires no vector DB setup, and is fully transparent. Embedding-based retrieval would be the right call at 50+ documents.

**Why two AI calls (diagnosis + self-check)?** The self-check step measurably catches JSON formatting errors and hallucinated bug descriptions. It costs one extra API call but raises reliability significantly.

**Why few-shot specialization?** Without the GlitchBot persona, Claude gives polite, generic answers. The few-shot examples enforce JSON structure, a consistent tone, and snarky comments — making the output measurably different and more useful in a game debugging context.

**Why Streamlit tabs?** Keeps the original game experience intact (Tab 1) while adding the AI features in a dedicated space (Tab 2), making the extension obvious to anyone reviewing the repo.

---

## 🧪 Testing Summary

- **18 unit tests** in `tests/test_game_logic.py` — all pass
- **8 eval harness test cases** — 7/8 pass (TC005 clean-code case produces minor false positives)
- **Guardrail tests** (TC006, TC007) correctly block empty and non-code inputs
- **Confidence scores** averaged 94% across successful agent runs
- **Key finding:** The AI occasionally over-diagnoses clean code. Adding a confidence threshold (< 0.7 → "No significant bugs found") would improve precision.

---

## 🔮 Reflection

This project taught me that AI reliability is an active choice, not a default. The self-check step felt redundant at first but caught two JSON formatting errors during testing. RAG grounding reduced hallucinated bug descriptions significantly compared to a baseline prompt with no context. The biggest challenge was getting consistent JSON output from the AI — few-shot examples in the system prompt were the most effective fix.

---

## 📁 File Structure
applied-ai-system-project/
├── app.py                  # Main Streamlit app (game + AI debug agent tabs)
├── logic_utils.py          # Core game logic (fixed from Module 1)
├── debug_agent.py          # 5-step agentic debug pipeline
├── rag_retriever.py        # RAG retrieval over glitch knowledge base
├── rag_knowledge_base.py   # 6 custom bug pattern documents
├── eval_harness.py         # Test harness / evaluation script
├── requirements.txt
├── README.md
├── model_card.md
├── assets/
│   └── architecture.png    # System architecture diagram
└── tests/
└── test_game_logic.py  # 18 pytest unit tests

---

## 🎬 Demo Walkthrough

*[<div style="position: relative; padding-bottom: 56.25%; height: 0;"><iframe src="https://www.loom.com/embed/9fb6949381dc414eaf41560dcacc595a" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>]

---

*Built with Python, Streamlit, and Anthropic Claude. Extended from CodePath AI110 Module 1.*
