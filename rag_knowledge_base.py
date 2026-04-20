GLITCH_KNOWLEDGE_BASE = [
    {
        "id": "KB001",
        "title": "Streamlit Session State Reset Bug",
        "tags": ["streamlit", "session_state", "reset", "state"],
        "description": (
            "In Streamlit, any variable not stored in st.session_state is re-initialized "
            "on every script re-run triggered by a widget interaction. This means a secret "
            "number assigned with `secret = random.randint(...)` outside session_state will "
            "change every time the user clicks a button."
        ),
        "fix": (
            "Use `if 'secret' not in st.session_state: st.session_state.secret = random.randint(...)` "
            "to initialize once and persist across reruns."
        ),
        "example_bad": "secret = random.randint(1, 100)  # resets every rerun",
        "example_good": "if 'secret' not in st.session_state:\n    st.session_state.secret = random.randint(1, 100)",
    },
    {
        "id": "KB002",
        "title": "Inverted Comparison Hints (Higher/Lower Bug)",
        "tags": ["logic", "comparison", "hints", "higher", "lower"],
        "description": (
            "A common logic inversion bug: the hint says 'Go Higher' when the guess is too high, "
            "and 'Go Lower' when the guess is too low. This happens when the > and < operators "
            "are swapped in the condition."
        ),
        "fix": (
            "Ensure: if guess > secret → 'Too High / Go Lower', "
            "if guess < secret → 'Too Low / Go Higher'."
        ),
        "example_bad": "if guess > secret:\n    return 'Too Low'  # WRONG",
        "example_good": "if guess > secret:\n    return 'Too High'  # CORRECT",
    },
    {
        "id": "KB003",
        "title": "String vs Integer Comparison Bug",
        "tags": ["type", "string", "integer", "comparison", "cast"],
        "description": (
            "Python string comparison uses lexicographic ordering, not numeric. "
            "Comparing str('9') > str('10') returns True because '9' > '1' lexicographically. "
            "This causes wrong outcomes in number games when the secret is accidentally cast to str."
        ),
        "fix": (
            "Always cast both values to int before comparing: "
            "`guess = int(guess); secret = int(secret)`."
        ),
        "example_bad": "if str(guess) > str(secret):  # '9' > '10' is True, BUG",
        "example_good": "if int(guess) > int(secret):  # 9 > 10 is False, CORRECT",
    },
    {
        "id": "KB004",
        "title": "Score Rewarding Wrong Guesses (Even Attempt Bug)",
        "tags": ["score", "logic", "points", "attempt", "even", "odd"],
        "description": (
            "A score function that checks `if attempt_number % 2 == 0` and awards bonus points "
            "on even attempts regardless of outcome will reward the player for wrong guesses "
            "on even-numbered attempts. This breaks the scoring incentive entirely."
        ),
        "fix": (
            "Only award points on a 'Win' outcome. "
            "Deduct points for 'Too High' or 'Too Low' outcomes."
        ),
        "example_bad": "if attempt_number % 2 == 0:\n    return current_score + 10  # rewards wrong guesses!",
        "example_good": "if outcome == 'Win':\n    return current_score + max(10, 100 - 10 * attempt_number)",
    },
    {
        "id": "KB005",
        "title": "Difficulty Range Inconsistency Bug",
        "tags": ["difficulty", "range", "hard", "easy", "normal", "inconsistency"],
        "description": (
            "When two places in the code define the difficulty range independently "
            "(e.g., once in a function and once inline), they can drift out of sync. "
            "For example, Hard mode returning 1-50 in one place but 1-100 in another "
            "means New Game and the initial game use different ranges."
        ),
        "fix": (
            "Define difficulty ranges in exactly one place (e.g., get_range_for_difficulty()) "
            "and always call that function — never hardcode ranges inline."
        ),
        "example_bad": "# In get_range_for_difficulty: Hard → (1, 50)\n# In New Game button: randint(1, 100)  # MISMATCH",
        "example_good": "low, high = get_range_for_difficulty(difficulty)\nst.session_state.secret = random.randint(low, high)",
    },
    {
        "id": "KB006",
        "title": "Input Not Validated Before Comparison",
        "tags": ["input", "validation", "parse", "non-numeric", "error"],
        "description": (
            "If user input is not validated before being compared to the secret number, "
            "non-numeric inputs (letters, symbols, empty string) will raise a ValueError "
            "or TypeError and crash the app."
        ),
        "fix": (
            "Use a parse_guess() function with try/except to catch invalid input "
            "and return a user-friendly error message instead of crashing."
        ),
        "example_bad": "guess = int(raw_input)  # crashes on 'abc'",
        "example_good": "ok, guess, err = parse_guess(raw_input)\nif not ok:\n    st.error(err)",
    },
]
 