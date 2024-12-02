from flask import Flask, jsonify, request
from collections import defaultdict
from solver.game_logic import get_feedback, filter_remaining_words_with_constraints
from solver.entropy import calculate_entropy
from solver.thompson import thompson_sample, update_beta_distributions
from utils.helpers import load_valid_guesses_csv, load_possible_words_txt, combine_with_word_list, load_word_frequencies
import random
import logging
from flask_cors import CORS
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import os
import json
import atexit


app = Flask(__name__)
CORS(app)
PRIOR_BETAS_FILE = os.path.join('game-data', 'prior_betas.json')
word_list = load_possible_words_txt()

# valid_guesses = list(load_valid_guesses_csv())
valid_words_dict = load_word_frequencies()


# valid_words_dict = combine_with_word_list(word_frenquency_dict, valid_guesses)

# We need this to persist despite each game state



def save_prior_betas():
    global prior_betas
    try:
        with open(PRIOR_BETAS_FILE, 'w') as f:
            json.dump(prior_betas, f)
        print("prior_betas successfully saved to file.")
    except Exception as e:
        print(f"Error saving prior_betas: {e}")

# Load prior_betas from file
def load_prior_betas():
    global prior_betas
    if os.path.exists(PRIOR_BETAS_FILE):
        try:
            with open(PRIOR_BETAS_FILE, 'r') as f:
                prior_betas = json.load(f)
            print("prior_betas successfully loaded from file.")
        except Exception as e:
            print(f"Error loading prior_betas: {e}")
            prior_betas = {guess: {"alpha": 1, "beta": 1} for guess in valid_words_dict.keys()}
    else:
        prior_betas = {guess: {"alpha": 1, "beta": 1} for guess in valid_words_dict.keys()}
        print("prior_betas initialized with default values.")

load_prior_betas()

# Initialize game state
def reset_game_state():
    return {
        "secret_word": None,       # Word to guess (set in `/new-game`)

        # Array of Letter objects [{}, {}, {}, {}, {}] in the form of
        # {key: Letter, value: Feedback[i]}
        "guesses": [],     # List of guesses and their feedback
        "score": 0,
        "remaining_words_dict": valid_words_dict,
        "solved": False,
        "num_remaining_words": len(valid_words_dict),
        "constraints": {
            "green": {},             # Positions where letters are green
            "yellow": defaultdict(set),  # Letters with restricted positions
            "gray": set()            # Letters that cannot be in the word
        },
        "phase": "waiting"
    }

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Wordle Solver API!"})

@app.route('/prior-betas/<word>', methods=['GET'])
def get_prior_betas(word):
    global prior_betas
    if word not in prior_betas:
        return jsonify({"error": f"Word '{word}' not found in prior betas."}), 404

    alpha = prior_betas[word]["alpha"]
    beta = prior_betas[word]["beta"]

    return jsonify({"word": word, "alpha": alpha, "beta": beta})

# API Endpoints (idk what im doing lowkey)
@app.route('/new-game', methods=['POST'])

def new_game():
    # Initialize the Geme State
    global game_state
    game_state = reset_game_state()
    game_state["secret_word"] = random.choice(word_list)
    game_state["phase"] = "guessing"

    secret_in_guess_pool = game_state["secret_word"] in valid_words_dict

    logging.debug(f"New game started with secret word: {game_state['secret_word']}")
    return jsonify({
        "message": "New game started!", 
        "word_count": game_state["num_remaining_words"], 
        "secret_in_guess_pool": secret_in_guess_pool
        }
    )


@app.route('/solution', methods=['GET'])
def get_solution():
    global game_state
    # Always reset the game state when `/solution` is called
    game_state = reset_game_state()
    game_state["secret_word"] = random.choice(word_list)
    game_state["phase"] = "guessing"
    logging.debug(f"New game started with secret word: {game_state['secret_word']}")
    
    return jsonify({
        "solution": game_state["secret_word"],
        "words_left": game_state["num_remaining_words"]
    })



@app.route('/recommend', methods=['GET'])
def recommend():
    global game_state
    if 'game_state' not in globals() or game_state is None:
        return jsonify({"error": "Game state is not initialized. Start a new game using /new-game."}), 400
    
    logging.debug(f"Game state: {game_state}")

    if "remaining_words_dict" not in game_state:
        return jsonify({"error": "'remaining_words_dict' not found in game state"}), 400

    # Check if the game is in the guessing phase
    if game_state["phase"] != "guessing":
        logging.error("Game is not in the guessing phase.")
        return jsonify({"error": "Game is not in the guessing phase."}), 400

    # Check if there are remaining words
    if not game_state["remaining_words_dict"]:
        logging.error("No remaining words! Cannot make a recommendation.")
        return jsonify({"error": "No remaining words! Cannot make a recommendation."}), 400

    # Core logic for generating a recommendation
    guess_pool = valid_words_dict
    solution_pool = game_state["remaining_words_dict"]
    flag = game_state['secret_word'] in guess_pool

    word_scores = {}
    word_probabilities = {}
    word_beta_distributions = {}
    combined_scores = {}

    # Compute scores for each word
    # Store in nested dict - This is so 106a coded :)
    for guess in tqdm(guess_pool, desc="Computing scores"):
        combined_scores[guess] = {}
        inner_scores = combined_scores[guess]

        entropy_score = calculate_entropy(guess, solution_pool)
        frequency_probability = game_state["remaining_words_dict"].get(guess, 0)
        sampled_probability = thompson_sample(prior_betas, guess)

        inner_scores["entropy"] = entropy_score
        inner_scores["thompson_sample"] = sampled_probability 
        inner_scores["inferenced_prob"] = frequency_probability

        # Calculate the combined score
        combined_score = 0.5 * entropy_score + 0.5 * (sampled_probability + frequency_probability)
        inner_scores["combined_score"] = combined_score


        # Store additional information for debugging or visualization
        word_scores[guess] = entropy_score
        word_probabilities[guess] = frequency_probability
        word_beta_distributions[guess] = prior_betas[guess]

    # Select the top K words based on the combined score
    k = 10
    top_k_words = sorted(combined_scores.keys(), key=lambda x: combined_scores[x]["combined_score"], reverse=True)[:k]

    # Prepare data for each top word
    top_k_data = []
    for word in top_k_words:
        top_k_data.append({
            "word": word,
            "combined_score": combined_scores[word]["combined_score"],
            "entropy": combined_scores[word]["entropy"],
            "thompson_sample": combined_scores[word]["thompson_sample"],
            "prior": combined_scores[word]["inferenced_prob"],
            "beta_distribution": word_beta_distributions[word]
        })

    return jsonify({
        "top_k_words": top_k_data,
        "top_word": top_k_words[0],
        "num_remaining_words": len(solution_pool),
        "secret_word": game_state["secret_word"],
        "sanity_check": flag
    })

# API Endpoints (idk what im doing lowkey)
@app.route('/guess', methods=['POST'])
def guess():

    """Submit a guess and receive feedback."""
    global game_state
    global prior_betas

    if 'game_state' not in globals() or game_state is None:
        return jsonify({"error": "Game state is not initialized. Start a new game using /new-game."}), 400
    
    data = request.json
    guess = data.get("guess")

    if game_state["phase"] != "guessing":
        return jsonify({"error": "Game is not in the guessing phase."}), 400
    
    if not guess or len(guess) != 5:
        return jsonify({"error": "Invalid guess! Must be a 5-letter word."}), 400

    if guess not in valid_words_dict:
        return jsonify({"error": "Invalid guess! Must be a valid English word."}), 400

    # Get feedback
    feedback = get_feedback(guess, game_state["secret_word"])
    game_state["guesses"].append({"guess": guess, "feedback": feedback})
    game_state["score"] += 1

    # Add logic to guess if the word is correct
    if feedback == [2, 2, 2, 2, 2]:
        game_state["solved"] = True
        game_state["phase"] = "solved"

        return jsonify({
            "message": "Congratulations! You solved it!",
            "score": game_state["score"],
            "guesses": game_state["guesses"],
            "feedback": feedback
        })
    
    # Don't let the guessed word be in the remaining words
    # del(game_state["remaining_words_dict"][guess])
    # Else, we have not finished the game yet!
    game_state["remaining_words_dict"] = filter_remaining_words_with_constraints(
        guess, feedback, game_state["remaining_words_dict"], game_state["constraints"])
    
    game_state["num_remaining_words"] = len(game_state["remaining_words_dict"])

    # for thompson sampling
    prior_betas = update_beta_distributions(prior_betas, game_state["remaining_words_dict"])
    
    return jsonify({
        "feedback": feedback,
        "remaining_words_dict": game_state["remaining_words_dict"],
        "num_remaining_words": len(game_state["remaining_words_dict"]),
        "guesses": game_state["guesses"],
    })

@app.route('/validate-word', methods=['POST'])
def validate_word():
    data = request.json
    word = data.get("word", "").lower()
    is_valid = word in valid_words_dict
    return jsonify({"valid": is_valid})




@app.route('/game-state', methods=['GET'])
def get_game_state():
    global game_state
    if 'game_state' not in globals() or game_state is None:
        return jsonify({"error": "Game state is not initialized. Start a new game using /new-game."}), 400

    """Retrieve the current game state."""
    return jsonify({
        "phase": game_state["phase"],
        "score": game_state["score"],
        "guesses": game_state["guesses"],
        "remaining_words": game_state["num_remaining_words"],
        "solved": game_state["solved"],
        "betas": prior_betas
    })

if __name__ == '__main__':
    load_prior_betas()  # Load on startup
    atexit.register(save_prior_betas)  # Save on shutdown
    app.run(debug=True)