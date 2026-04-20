🃏 Model Card — Game Glitch Investigator: AI Debug Agent
Model Overview
FieldValueModel Usedclaude-sonnet-4-20250514 (Anthropic)TaskCode bug diagnosis for Python game codeInterfaceStreamlit web app + CLI eval harnessBase Projectai110-module1show-gameglitchinvestigator-starter (CodePath AI110)

🎯 Intended Use
This system is designed to help students and beginner developers identify common bugs in Python Streamlit game code. It specializes in a curated set of six bug patterns documented in the Glitch Knowledge Base. It is not a general-purpose code review tool.

⚠️ Limitations and Biases
Knowledge base bias: The RAG knowledge base contains only 6 bug patterns, all specific to Streamlit number-guessing games. Code outside this domain (e.g., web APIs, databases, machine learning pipelines) will receive generic or irrelevant diagnoses.
Hallucination risk: Even with RAG grounding, the AI occasionally identifies bugs in clean code. During testing, the clean-code test case (TC005) received a low-severity diagnosis 60% of the time. This is a known limitation of current LLMs.
Persona bias: The GlitchBot few-shot persona uses sarcastic language. In an educational setting, this tone may discourage some learners. A production version should offer a toggle between snarky and professional modes.
No syntax execution: The agent reads code as text — it does not run it. A real static analyzer (e.g., pylint, ast module) would catch bugs the AI misses.
API dependency: The system requires an active Anthropic API key and internet access. It cannot run fully offline.

🚨 Misuse Potential and Prevention
Potential misuse: A student could paste an entire assignment into the agent and use the diagnosis to complete their work without understanding the bugs themselves.
Prevention: The system is intentionally scoped to game-specific bug patterns. It would not diagnose arbitrary assignment code effectively. A deployed version could add a disclaimer: "This tool explains bugs — it does not fix your code for you." Rate limiting and logging (already implemented via agent.log) would also deter abuse.

😲 Surprising Testing Results
The most surprising finding was how confidently the AI diagnosed bugs it couldn't actually verify. On TC003 (string comparison bug), the agent gave a 97% confidence score even though it only saw a 3-line snippet with no runtime evidence. This overconfidence is why the self-check step matters — it acts as a second opinion and occasionally lowers the final confidence score to a more honest level.
Another surprise: the guardrail for non-code text (TC007: "hello world this is not code at all") was tripped correctly, but a snippet like x = hello passed the guardrail because it contains =. A smarter guardrail would use Python's ast.parse() to validate syntax.

🤝 AI Collaboration During Development
How AI was used
Claude was used throughout this project for: designing the agent pipeline architecture, writing the few-shot examples for GlitchBot's persona, debugging the JSON stripping logic in debug_agent.py, drafting the knowledge base entries, and generating the eval harness test case structure.
✅ Helpful AI suggestion
When designing the self-check step, Claude suggested using a separate system prompt with no persona (no GlitchBot tone) for the verifier role — "a senior code reviewer." This was excellent advice. The neutral verifier prompt produced more calibrated confidence corrections than using GlitchBot for both steps, which tended to agree with itself too readily.
❌ Flawed AI suggestion
Claude initially suggested using cosine_similarity from sklearn for the RAG retrieval step, recommending I embed each document and the query using sentence-transformers. While this would work better at scale, it introduced a 500MB dependency for a 6-document knowledge base. The keyword-scoring approach I implemented instead is more transparent, faster to load, and requires zero additional dependencies — the AI was optimizing for technical sophistication over practical fit.

📊 Evaluation Results
TestResultConfidenceTC001 — State Reset Bug✅ Pass99%TC002 — Inverted Hints✅ Pass97%TC003 — String Comparison Bug✅ Pass95%TC004 — Score Bug✅ Pass93%TC005 — Clean Code⚠️ Minor false positive72%TC006 — Empty Input Guardrail✅ Pass (blocked)—TC007 — Non-Code Guardrail✅ Pass (blocked)—TC008 — Difficulty Range Bug✅ Pass91%
Overall: 7/8 pass (88%) | Avg confidence on successful runs: 94%

🔮 Future Improvements

Replace keyword RAG with embedding-based retrieval (FAISS + sentence-transformers) once the KB grows beyond ~20 documents
Add ast.parse() guardrail to validate Python syntax before the AI call
Add a confidence threshold: if final_confidence < 0.70, display "No significant bugs found" instead of a low-confidence diagnosis
Implement a tone toggle: Professional / Snarky
Expand knowledge base to cover Flask, FastAPI, and general Python anti-patterns
Add multi-file support so users can paste an entire project and the agent reasons across files