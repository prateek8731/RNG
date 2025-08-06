import random
import hashlib
import time
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare, norm, pearsonr

# Configuration
NUMBERS_RANGE = range(1, 51)
DRAW_SIZE = 7
BONUS_RANGE = range(1, 51)
SEED_LENGTH = 32

# History of past draws (example format)
HISTORY = [
    [4, 8, 12, 26, 29, 33, 37],
    # Add previous draws here
]

# --- RNG Engine ---
def generate_seed():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()

def secure_seed(seed):
    random.seed(seed)

def draw_numbers():
    main = random.sample(NUMBERS_RANGE, DRAW_SIZE)
    bonus = random.choice(BONUS_RANGE)
    return sorted(main), bonus

# --- Statistical Tests ---
def frequency_test(draws):
    all_numbers = [num for draw in draws for num in draw]
    counts = Counter(all_numbers)
    expected = len(all_numbers) / len(NUMBERS_RANGE)
    observed = [counts.get(i, 0) for i in NUMBERS_RANGE]
    stat, p = chisquare(observed)
    return stat, p

def run_test(draws):
    binary_seq = []
    mean = np.mean([num for draw in draws for num in draw])
    for draw in draws:
        for num in draw:
            binary_seq.append(1 if num > mean else 0)

    runs = 1
    for i in range(1, len(binary_seq)):
        if binary_seq[i] != binary_seq[i - 1]:
            runs += 1

    n = len(binary_seq)
    pi = sum(binary_seq) / n
    expected_runs = 2 * n * pi * (1 - pi) + 1
    std_dev = np.sqrt(2 * n * pi * (1 - pi) * (2 * n * pi * (1 - pi) - 1) / (n - 1))
    z = (runs - expected_runs) / std_dev
    p = 2 * (1 - norm.cdf(abs(z)))
    return runs, expected_runs, z, p

# --- Prediction Simulation ---
def similarity_to_history(candidate):
    similarities = []
    for hist in HISTORY:
        match = len(set(candidate).intersection(set(hist)))
        similarities.append(match)
    return max(similarities)

def predict_high_confidence(count=3):
    candidates = []
    while len(candidates) < count:
        numbers, bonus = draw_numbers()
        if similarity_to_history(numbers) <= 2:
            candidates.append((numbers, bonus))
    return candidates

# --- Example Execution ---
if __name__ == '__main__':
    # Seeding and Drawing
    seed = generate_seed()
    secure_seed(seed)
    main_numbers, bonus_number = draw_numbers()
    print("Generated Numbers:", main_numbers, "+ Bonus:", bonus_number)

    # Statistical Testing
    print("\n--- Frequency Test ---")
    stat, p = frequency_test(HISTORY + [main_numbers])
    print(f"Chi-square statistic: {stat:.2f}, p-value: {p:.4f}")

    print("\n--- Run Test ---")
    runs, expected, z, p_run = run_test(HISTORY + [main_numbers])
    print(f"Runs: {runs}, Expected Runs: {expected:.2f}, Z: {z:.2f}, p-value: {p_run:.4f}")

    print("\n--- High Confidence Predictions ---")
    predictions = predict_high_confidence()
    for idx, (nums, bonus) in enumerate(predictions):
        print(f"Prediction {idx+1}: {nums} + Bonus: {bonus}")
