def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIX: Hard was returning 1-50 but New Game was using 1-100 — unified here
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 500
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # FIX: Refactored from app.py using Copilot Agent mode
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIXME: Logic breaks here — original code had hints backwards
    # FIX: Ensure both values are integers before comparing to avoid
    # string-based ordering bugs (e.g. "9" > "10" is True in Python)
    # Also fixed swapped hints: > secret means Too High, not Too Low
    try:
        guess = int(guess)
        secret = int(secret)
    except (TypeError, ValueError):
        return "Error", "⚠️ Could not compare values."

    if guess == secret:
        return "Win", "🎉 Correct!"
    elif guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # FIXME: Logic breaks here — even attempts were rewarding wrong guesses
    # FIX: Removed the even/odd attempt bonus that was adding points for wrong guesses
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score