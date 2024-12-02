from utils.helpers import normalize
from collections import defaultdict

def get_feedback(guess, answer):
    """Generate feedback for a guess compared to the answer."""
    feedback = []
    answer_list = list(answer)  # Convert to a mutable list of characters

    # First pass: Check for 'green'
    for idx, char in enumerate(guess):
        if char == answer[idx]:
            feedback.append(2)
            answer_list[idx] = None 
        else:
            feedback.append(None)  # Placeholder for yellows/greys


    # Second pass: Check for 'yellow' and 'gray'
    for idx, char in enumerate(guess):
        if feedback[idx] is None: 
            if char in answer_list:
                feedback[idx] = 1
                answer_list[answer_list.index(char)] = None  
            else:
                feedback[idx] = 0
    return feedback



def filter_remaining_words_with_constraints(guess, feedback, remaining_words_dict, constraints):
    """
    Narrow down the list of possible words based on the cumulative constraints.
    """
    # Create a mutable copy of the guess and feedback to track processed letters
    processed_positions = set()
    
    # First pass: Process green (2) feedback
    for i, (g_letter, f) in enumerate(zip(guess, feedback)):
        if f == 2:  # Green
            constraints['green'][i] = g_letter
            processed_positions.add(i)

    # Second pass: Process yellow (1) and gray (0) feedback
    for i, (g_letter, f) in enumerate(zip(guess, feedback)):
        if i in processed_positions:
            continue  # Skip positions already processed as green

        if f == 1:  # Yellow
            # Ensure the letter isn't already satisfying a green constraint
            if g_letter not in constraints['green'].values():
                constraints['yellow'][g_letter].add(i)
        elif f == 0:  # Gray
            # Gray only applies if the letter is not already green or yellow
            if g_letter not in constraints['green'].values() and g_letter not in constraints['yellow'].keys():
                constraints['gray'].add(g_letter)

    # Filter the remaining words
    filtered_words = {}
    for word in remaining_words_dict.keys():
        if is_valid_word(word, constraints):
            filtered_words[word] = remaining_words_dict[word]

    return normalize(filtered_words)


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