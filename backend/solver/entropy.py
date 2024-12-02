import math
from solver.game_logic import get_feedback

def calculate_entropy(guess, solution_pool):
    """
    Calculate the entropy of a guess given the current solution pool.
    """
    feedback_counts = {}
    total_words = len(solution_pool)

    # Simulate feedback for each word in the solution pool
    for solution in solution_pool.keys():
        feedback = tuple(get_feedback(guess, solution))  # Simulate feedback
        if feedback not in feedback_counts:
            feedback_counts[feedback] = 0
        feedback_counts[feedback] += 1

    # Calculate entropy
    entropy = 0
    for count in feedback_counts.values():
        probability = count / total_words
        entropy -= probability * math.log2(probability)
    return entropy

