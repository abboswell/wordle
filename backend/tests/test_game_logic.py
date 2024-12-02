import pytest
from solver.game_logic import get_feedback, filter_remaining_words_with_constraints
from utils.helpers import load_valid_guesses_csv, load_possible_words_txt, load_word_frequencies, combine_with_word_list
from collections import defaultdict

"""
Testing load_words
"""
def test_load_valid_guesses_success():
    words = load_valid_guesses_csv()
    assert isinstance(words, list)
    assert len(words) > 0
    assert all(isinstance(word, str) for word in words)
    assert all(word.islower() for word in words)

def test_load_possible_words_success(): 
    words = load_possible_words_txt()
    assert isinstance(words, list)
    assert len(words) > 0
    assert all(isinstance(word, str) for word in words)
    assert all(word.islower() for word in words)



def test_combine_dict():
    words = load_possible_words_txt()
    word_frequencies = load_word_frequencies()
    new_dict = combine_with_word_list(word_frequencies, words)
    assert(len(new_dict.keys()) == len(words))
    assert(all(word in words for word in new_dict.keys()))



"""
TESTING GET_FEEDBACK
"""



def test_get_feedback_all_correct():
    """Test when the guess matches the answer exactly."""
    assert get_feedback("apple", "apple") == [2, 2, 2, 2, 2]

def test_get_feedback_some_correct():
    """Test when some letters are correct and in the correct position."""
    assert get_feedback("apple", "ample") == [2, 0, 2, 2, 2]

def test_get_feedback_all_wrong():
    """Test when no letters in the guess match the answer."""
    assert get_feedback("apple", "grape") == [1, 1, 0, 0, 2]

def test_get_feedback_repeated_letters_in_guess():
    """Test when the guess contains repeated letters not all present in the answer."""
    assert get_feedback("apple", "alike") == [2, 0, 0, 1, 2]

def test_get_feedback_repeated_letters_in_answer():
    """Test when the answer contains repeated letters."""
    assert get_feedback("llama", "alpha") == [0, 2, 1, 0, 2]

def test_get_feedback_no_matches():
    """Test when none of the guessed letters are in the answer."""
    assert get_feedback("apple", "zebra") == [1, 0, 0, 0, 1]

def test_get_feedback_empty_guess():
    """Test when the guess is an empty string."""
    assert get_feedback("", "apple") == []

def test_get_feedback_case_sensitivity():
    """Test that the function is case-sensitive."""
    assert get_feedback("Apple", "apple") == [0, 2, 2, 2, 2]

def test_get_feedback_guess_contains_extra_letters():
    """Test when the guess contains letters not present in the answer."""
    assert get_feedback("swift", "style") == [2, 0, 0, 0, 1]

def test_get_feedback_duplicate_guess_in_single_position():
    """Test when the guess contains duplicate letters in a single position."""
    assert get_feedback("bobby", "happy") == [0, 0, 0, 0, 2]



"""
TESTING FILTER_REMAINING_WORDS_WITH_CONSTRAINTS
"""


import pytest
from solver.game_logic import filter_remaining_words_with_constraints

@pytest.fixture
def setup_constraints():
    """
    Fixture to provide initial constraints.
    """
    return {
        "green": {},              # Positions where letters are green
        "yellow": defaultdict(set),  # Letters with restricted positions
        "gray": set(),             # Letters that cannot be in the word
    }

@pytest.fixture
def setup_remaining_words():
    """
    Fixture to provide initial remaining words dictionary.
    """
    return {
        "apple": 1,
        "ample": 1,
        "alike": 1,
        "alpha": 1,
        "zebra": 1,
        "bobby": 1,
    }

def is_valid_word(word, constraints):
    """
    Check if a word satisfies all the constraints.
    """
    # Check green constraints
    for i, letter in constraints['green'].items():
        if word[i] != letter:
            return False

    # Check yellow constraints
    for letter, restricted_positions in constraints['yellow'].items():
        if letter not in word:
            return False
        if any(word[i] == letter for i in restricted_positions):
            return False

    # Check gray constraints
    for letter in constraints['gray']:
        if letter in word:
            return False

    return True

def normalize(words):
    """
    Mock implementation of normalize for testing purposes.
    Replace this with the actual implementation if required.
    """
    return words

def test_is_valid_word_green():
    constraints = {"green": {0: "a"}, "yellow": defaultdict(set), "gray": set()}
    assert is_valid_word("apple", constraints) is True
    assert is_valid_word("ample", constraints) is True
    assert is_valid_word("zebra", constraints) is False


def test_filter_green_constraint(setup_remaining_words):
    """
    Test filtering when a green constraint is added.
    """
    guess = "apple"
    feedback = [2, 0, 0, 0, 0]  # 'a' is correct and in the right position
    constraints = {"green": {0: "a"}, "yellow": defaultdict(set), "gray": set()}
    filtered = filter_remaining_words_with_constraints(guess, feedback, setup_remaining_words, constraints)
    assert filtered == {}
    assert constraints["green"] == {0: "a"}
    assert constraints["gray"] == {"p", "l", "e"}


def test_filter_yellow_constraint(setup_constraints, setup_remaining_words):
    """
    Test filtering when a yellow constraint is added.

        "apple": 1,
        "ample": 1,
        "alike": 1,
        "alpha": 1,
        "zebra": 1,
        "bobby": 1,
    """
    guess = "apple"
    feedback = [1, 0, 0, 0, 1]  # 'p' is correct but in the wrong position
    constraints = setup_constraints
    filtered = filter_remaining_words_with_constraints(guess, feedback, setup_remaining_words, constraints)
    assert "zebra" in filtered
    assert "alike" not in filtered
    assert "alpha" not in filtered
    assert constraints["yellow"]['a'] == {0}
    assert constraints["yellow"]['e'] == {4}


def test_filter_gray_constraint(setup_constraints, setup_remaining_words):
    """
    Test filtering when a gray constraint is added.
    """
    guess = "apple"
    feedback = [0, 0, 0, 0, 0]  # None of the letters in 'apple' are in the word
    constraints = setup_constraints
    filtered = filter_remaining_words_with_constraints(guess, feedback, setup_remaining_words, constraints)
    assert "zebra" not in filtered
    assert "apple" not in filtered
    assert "ample" not in filtered
    assert constraints["gray"] == {"a", "p", "l", "e"}


def test_filter_mixed_constraints(setup_constraints, setup_remaining_words):
    """
    Test filtering with mixed constraints (green, yellow, and gray).
    """
    guess = "apple"
    feedback = [2, 1, 0, 1, 0]  # 'a' is green, 'p' is yellow, others are gray
    constraints = setup_constraints
    filtered = filter_remaining_words_with_constraints(guess, feedback, setup_remaining_words, constraints)
    assert "ample" not in filtered
    assert "apple" not in filtered
    assert "alike" not in filtered
    assert "alpha" in filtered
    assert constraints["green"] == {0: "a"}
    assert constraints["yellow"]["p"] == {1}
    assert constraints["gray"] ==  {"e"}


def test_empty_remaining_words(setup_constraints):
    """
    Test when there are no remaining words to filter.
    """
    guess = "apple"
    feedback = [2, 1, 0, 0, 0]
    remaining_words = {}
    constraints = setup_constraints
    filtered = filter_remaining_words_with_constraints(guess, feedback, remaining_words, constraints)
    assert filtered == {}


def test_no_constraints(setup_constraints, setup_remaining_words):
    """
    Test when no feedback constraints are applied (all gray).
    """
    guess = "zzzzz"
    feedback = [0, 0, 0, 0, 0]  # All gray feedback
    constraints = setup_constraints
    filtered = filter_remaining_words_with_constraints(guess, feedback, setup_remaining_words, constraints)
    assert len(filtered) == len(setup_remaining_words) - 1  # No filtering
    assert constraints["gray"] == {"z"}

def test_constraints_with_repeated_letters(setup_constraints, setup_remaining_words):
    """
    Test when the guess contains repeated letters.
    """
    guess = "bobby"
    feedback = [0, 0, 2, 0, 0]  # 'b' in position 2 is green
    constraints = setup_constraints
    filtered = filter_remaining_words_with_constraints(guess, feedback, setup_remaining_words, constraints)
    assert "bobby" not in filtered
    assert constraints["green"] == {2: "b"}
    assert constraints["gray"] == {"o", "y"}



"""

"""