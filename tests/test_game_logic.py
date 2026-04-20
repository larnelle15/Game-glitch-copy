"""
tests/test_game_logic.py
Unit tests for core game logic functions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score
 
 
# ── check_guess tests ──────────────────────────────────────────────────────────
def test_winning_guess():
    outcome, msg = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in msg
 
def test_guess_too_high():
    outcome, msg = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in msg
 
def test_guess_too_low():
    outcome, msg = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in msg
 
def test_check_guess_string_inputs():
    """Should handle string inputs by casting to int."""
    outcome, _ = check_guess("50", "50")
    assert outcome == "Win"
 
def test_check_guess_invalid_input():
    outcome, msg = check_guess("abc", 50)
    assert outcome == "Error"
    assert "Could not compare" in msg
 
 
# ── parse_guess tests ──────────────────────────────────────────────────────────
def test_parse_valid_integer():
    ok, val, err = parse_guess("42")
    assert ok is True
    assert val == 42
    assert err is None
 
def test_parse_float_rounds():
    ok, val, err = parse_guess("7.9")
    assert ok is True
    assert val == 7
 
def test_parse_empty_string():
    ok, val, err = parse_guess("")
    assert ok is False
    assert val is None
    assert "Enter a guess" in err
 
def test_parse_none():
    ok, val, err = parse_guess(None)
    assert ok is False
 
def test_parse_non_numeric():
    ok, val, err = parse_guess("hello")
    assert ok is False
    assert "not a number" in err.lower()
 
 
# ── get_range_for_difficulty tests ─────────────────────────────────────────────
def test_range_easy():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20
 
def test_range_normal():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 100
 
def test_range_hard():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 500
 
def test_range_unknown_defaults():
    low, high = get_range_for_difficulty("Unknown")
    assert low == 1
    assert high == 100
 
 
# ── update_score tests ─────────────────────────────────────────────────────────
def test_score_win_attempt_1():
    score = update_score(0, "Win", 1)
    assert score > 0
 
def test_score_wrong_guess_deducts():
    score = update_score(100, "Too High", 3)
    assert score == 95
 
def test_score_too_low_deducts():
    score = update_score(100, "Too Low", 2)
    assert score == 95
 
def test_score_minimum_win_points():
    """Even at many attempts, win should award at least 10 points."""
    score = update_score(0, "Win", 20)
    assert score >= 10
 