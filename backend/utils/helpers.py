import pandas as pd
import numpy as np

VALID_GUESSES_CSV = "game-data/valid_guesses.csv"
POSSILE_WORDS = "game-data/words.txt"

def load_valid_guesses_csv():
    VALID_GUESSES_CSV = "game-data/valid_guesses.csv"

    try:
        df = pd.read_csv(VALID_GUESSES_CSV)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {VALID_GUESSES_CSV}")
    
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
    
    if 'word' not in df.columns:
        raise ValueError("Expected column 'word' not found in the CSV file.")
    
    if df.empty:
        raise ValueError("The provided CSV file is empty.")
    
    return list(df['word'].str.lower())



def load_possible_words_txt():
    POSSILE_WORDS = "game-data/possible_words.txt"

    try:
        with open(POSSILE_WORDS, 'r') as file:
            words = file.read().splitlines()
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {POSSILE_WORDS}")
    
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
    
    if not words:
        raise ValueError("The provided text file is empty.")
    
    return words

def load_word_frequencies():
    WORD_FREQUENCIES = "game-data/word_frequency_map.txt"

    word_probabilities = {}
    with open(WORD_FREQUENCIES, 'r') as f:
        for line in f:
            parts = line.split()
            word = parts[0]
            frequencies = list(map(float, parts[1:]))
            # Calculate the average of the last 10 frequencies
            if len(frequencies) >= 10:
                avg_prob = np.mean(frequencies[-10:])
            else:
                avg_prob = np.mean(frequencies)  # Use all if fewer than 10 values exist
            word_probabilities[word] = avg_prob
    return word_probabilities

def normalize(pmf):
    print(f"Words before normalization: {list(pmf.keys())[:10]}")
    total = sum(pmf.values())
    if total == 0:
        return {word: 0 for word in pmf}
    return {word: prob / total for word, prob in pmf.items()}



def combine_with_word_list(word_probs, words_list):
    """Creates a dictionary with keys from words_list, using probabilities from word_probs."""
    result = {}
    for word in words_list:
        if word in word_probs:
            result[word] = word_probs[word]
        else:
            result[word] = 0  # Assign a default probability for missing words
    return normalize(result)