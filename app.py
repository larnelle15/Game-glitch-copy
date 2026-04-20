"""
app.py
Game Glitch Investigator — Applied AI System
Extended from Module 1 base project.
Now includes: AI Debug Agent tab with RAG + Agentic Workflow + Specialization.
"""
 
import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score
from debug_agent import run_debug_agent
 
st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮", layout="wide")
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)
 
attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}
attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)
 
st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
st.sidebar.divider()
st.sidebar.markdown("**About**")
st.sidebar.caption(
    "This app extends the Module 1 Game Glitch Investigator "
    "with a full AI Debug Agent powered by RAG, agentic reasoning, "
    "and specialized prompting."
)
 
# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎮 Play the Game", "🕵️ AI Debug Agent"])
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — The Game
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.title("🎮 Game Glitch Investigator: The Impossible Guesser")
    st.caption("An AI-generated guessing game — now actually fixed.")
 
    # Session state init
    if "secret" not in st.session_state:
        st.session_state.secret = random.randint(low, high)
    if "attempts" not in st.session_state:
        st.session_state.attempts = 1
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "status" not in st.session_state:
        st.session_state.status = "playing"
    if "history" not in st.session_state:
        st.session_state.history = []
 
    st.subheader("Make a guess")
    st.info(
        f"Guess a number between **{low}** and **{high}**. "
        f"Attempts left: **{attempt_limit - st.session_state.attempts + 1}**"
    )
 
    with st.expander("🔧 Developer Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts used:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)
 
    raw_guess = st.text_input("Enter your guess:", key=f"guess_input_{difficulty}")
    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.button("Submit Guess 🚀")
    with col2:
        new_game = st.button("New Game 🔁")
    with col3:
        show_hint = st.checkbox("Show hint", value=True)
 
    if new_game:
        st.session_state.attempts = 1
        st.session_state.secret = random.randint(low, high)
        st.session_state.status = "playing"
        st.session_state.history = []
        st.session_state.score = 0
        st.success("New game started!")
        st.rerun()
 
    if st.session_state.status != "playing":
        if st.session_state.status == "won":
            st.success("🏆 You already won! Start a new game to play again.")
        else:
            st.error("💀 Game over. Start a new game to try again.")
        st.stop()
 
    if submit:
        st.session_state.attempts += 1
        ok, guess_int, err = parse_guess(raw_guess)
        if not ok:
            st.session_state.history.append(raw_guess)
            st.error(err)
        else:
            st.session_state.history.append(guess_int)
            outcome, message = check_guess(guess_int, st.session_state.secret)
            if show_hint:
                st.warning(message)
            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )
            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                st.success(
                    f"🎉 You won! The secret was **{st.session_state.secret}**. "
                    f"Final score: **{st.session_state.score}**"
                )
            elif st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"😵 Out of attempts! The secret was **{st.session_state.secret}**. "
                    f"Score: **{st.session_state.score}**"
                )
 
    st.divider()
    st.caption("Built by an AI that claims this code is production-ready. (We fixed it anyway.)")
 
 
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AI Debug Agent
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.title("🕵️ AI Debug Agent")
    st.markdown(
        "Paste any Python game code below. The AI Debug Agent will:\n"
        "1. 🛡️ **Validate** your input\n"
        "2. 📚 **Retrieve** relevant bug patterns from the Glitch Knowledge Base (RAG)\n"
        "3. 🤖 **Diagnose** bugs using specialized AI (GlitchBot)\n"
        "4. 🔍 **Self-check** its own diagnosis for accuracy\n"
        "5. 🏁 **Return** a structured result with confidence score"
    )
 
    st.divider()
 
    # Prefill examples
    example_snippets = {
        "Select an example...": "",
        "State Reset Bug": "secret = random.randint(1, 100)\n# This runs every time a button is clicked",
        "Inverted Hints Bug": "if guess > secret:\n    return 'Too Low'\nelif guess < secret:\n    return 'Too High'",
        "String Comparison Bug": "if str(guess) > str(secret):\n    return 'Too High'",
        "Score Bug": "if attempt_number % 2 == 0:\n    return current_score + 10",
        "Paste your own code": "",
    }
 
    selected = st.selectbox("Try a pre-loaded example:", list(example_snippets.keys()))
    prefill = example_snippets.get(selected, "")
 
    code_input = st.text_area(
        "Paste Python code snippet here:",
        value=prefill,
        height=200,
        placeholder="e.g. paste a function or a few lines from your game...",
    )
 
    analyze_btn = st.button("🔍 Analyze with AI Agent", type="primary")
 
    if analyze_btn:
        if not code_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Running AI Debug Agent pipeline..."):
                result = run_debug_agent(code_input)
 
            st.divider()
            st.subheader("🔬 Agent Pipeline Steps")
 
            # Show observable intermediate steps
            for step in result.get("steps", []):
                if step.startswith("✅"):
                    st.success(step)
                elif step.startswith("❌"):
                    st.error(step)
                elif step.startswith("🛡️") or step.startswith("📚") or step.startswith("🤖") or step.startswith("🔍") or step.startswith("🏁"):
                    st.info(step)
                else:
                    st.write(step)
 
            st.divider()
 
            if not result["success"]:
                st.error(f"❌ Agent failed: {result.get('error', 'Unknown error')}")
            else:
                diagnosis = result["diagnosis"]
                self_check_result = result["self_check"]
                confidence = result.get("final_confidence", 0)
 
                # Diagnosis card
                st.subheader("🐛 Diagnosis")
                severity = diagnosis.get("severity", "Unknown")
                severity_color = {
                    "Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"
                }.get(severity, "⚪")
 
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**Severity:** {severity_color} {severity}")
                    bugs = diagnosis.get("bugs_found", [])
                    if bugs:
                        st.markdown("**Bugs Found:**")
                        for bug in bugs:
                            st.markdown(f"- {bug}")
                    st.markdown(f"**Fix Suggestion:** {diagnosis.get('fix_suggestion', 'N/A')}")
                    st.markdown(f"> 😏 *{diagnosis.get('snarky_comment', '')}*")
                with col_b:
                    st.metric("Final Confidence", f"{confidence:.0%}")
                    verified = self_check_result.get("verified", False)
                    st.metric("Self-Check", "✅ Passed" if verified else "⚠️ Flagged")
                    if not verified:
                        st.caption(self_check_result.get("corrections", ""))
 
                # Raw JSON expander
                with st.expander("📄 Raw Agent Output (JSON)"):
                    st.json(result)
 
    st.divider()
    st.caption("GlitchBot — powered by RAG + Agentic Workflow + Specialized Prompting")