# 💭 Reflection: Game Glitch Investigator

> Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

---

## 1. What was broken when you started?

The first time I ran the game it looked fine on the surface — there was a number input, a submit button, and difficulty settings in the sidebar. But once I actually started playing, things got weird fast. The hints were backwards: I'd guess a number that was clearly too high and the game would tell me to "Go Higher," which made no sense. On top of that, the Hard difficulty range showed 1–50 in the sidebar but the game was secretly using 1–100 under the hood, so the range you were told and the range the game actually used didn't match. There was also a scoring bug where guessing wrong on an even-numbered attempt would actually *add* points instead of taking them away, which completely broke the point of having a score.

**Concrete bugs noticed:**
- The `check_guess` function had its "Too High" and "Too Low" hints swapped — guessing above the secret returned "Go Higher" instead of "Go Lower."
- Every other attempt, the secret number was being converted to a string before comparison, which caused string-based comparisons (`"9" > "10"` is `True` in Python) and made hints unpredictable.
- The Hard difficulty was configured with a range of 1–50 in `get_range_for_difficulty`, but the New Game button always reset using `random.randint(1, 100)`, ignoring difficulty entirely.

---

## 2. How did you use AI as a teammate?

I used Claude (via claude.ai) to help me understand the buggy logic and plan my fixes. I pasted in the full `app.py` and `logic_utils.py` and asked it to walk me through what was going wrong in `check_guess` and why the hints didn't match the guesses.

**Correct AI suggestion:** Claude correctly identified that on even-numbered attempts, the code was doing `secret = str(st.session_state.secret)` before passing it into `check_guess`, which caused Python to compare an `int` guess against a `str` secret using string ordering rules. That explained exactly why hints were randomly wrong on every other guess. I verified this by reading the block in `app.py` around line 95 and confirming the `if st.session_state.attempts % 2 == 0` branch was doing exactly that.

**Incorrect/misleading AI suggestion:** At one point Claude suggested I could fix the string comparison issue by converting both values to strings consistently throughout `check_guess`. That would have made comparisons consistent but would have introduced a different bug — string ordering of numbers is wrong (e.g. `"9" > "10"` evaluates to `True`). I caught this by thinking through a few test cases manually before applying the suggestion, and instead fixed it by removing the string conversion entirely and keeping both values as integers.

---

## 3. Debugging and testing your fixes

My main way of checking whether a bug was fixed was to run the game with `streamlit run app.py` and test edge cases directly — specifically guessing numbers I knew were higher or lower than the secret (visible in the Developer Debug Info expander) and confirming the hint matched. I also wrote a `pytest` test in `tests/test_game_logic.py` that called `check_guess(60, 50)` and asserted the outcome was `"Too High"`, and another that called `check_guess(30, 50)` and asserted `"Too Low"`. Both tests failed before the fix and passed after, which gave me confidence the logic was corrected. I also tested the Hard difficulty new game flow by clicking "New Game" several times and checking the debug panel to confirm the secret stayed within 1–50.

AI did help me think through the test structure — Claude suggested the pattern of testing one specific input/output pair per test function rather than trying to test everything in one big test, which made the tests much easier to read and debug when something failed.

---

## 4. What did you learn about Streamlit and state?

The secret number kept changing because Streamlit reruns the entire Python script from top to bottom every single time something happens on the page — a button click, a text input change, anything. Without `st.session_state`, the line `random.randint(low, high)` would run again on every rerun and generate a brand new secret each time, so you'd never be guessing against the same number twice.

Streamlit "reruns" are basically Streamlit's way of reacting to user input — instead of updating just one part of the page, it re-executes the whole script. Think of it like refreshing a webpage every time you click a button, except the page rebuilds itself from your code. `st.session_state` is like a small memory that survives those refreshes — anything you store in it stays put across reruns. The fix that stabilized the secret number was wrapping the `random.randint` call in an `if "secret" not in st.session_state:` check, so it only generates a new number once at the start of a game, and after that, `st.session_state.secret` holds the same value no matter how many times the page reruns.

---

## 5. Looking ahead: your developer habits

One habit I want to carry forward is reading the actual code carefully before blindly applying an AI suggestion — the string-vs-integer comparison bug would have gotten worse if I'd just accepted Claude's first fix without thinking it through. That moment reminded me that AI is a useful thinking partner but not a replacement for understanding the code yourself.

Next time I work with AI on a coding task, I'd give it more specific context upfront instead of pasting everything and asking a vague question. When I narrowed my prompt to "explain exactly what happens on line 95 of app.py when attempts is even," I got a much more useful answer than when I asked "why are the hints wrong."

This project shifted how I think about AI-generated code — it's not that the code is obviously broken or obviously fine, it's that it can look completely reasonable and still have subtle logical bugs that only show up in specific situations. You have to actually play with it, test it, and question it, not just read it and assume it works.