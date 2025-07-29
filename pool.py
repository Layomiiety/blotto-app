import numpy as np
import pandas as pd

NUM_CASTLES = 10
TOTAL_SOLDIERS = 100
BASELINE_MIN = 2  # each castle gets at least 2 soldiers

def normalize_allocation_with_min(weights, min_per_castle=BASELINE_MIN):
    base = np.full(NUM_CASTLES, min_per_castle)
    remaining = TOTAL_SOLDIERS - base.sum()
    if remaining < 0:
        raise ValueError("Minimum allocation exceeds total soldier count.")
    weights = np.array(weights, dtype=np.float64)
    weights = weights / weights.sum() * remaining
    rounded = np.floor(weights).astype(int)
    remainder = remaining - rounded.sum()
    frac = weights - rounded
    indices = np.argsort(-frac)
    for i in range(remainder):
        rounded[indices[i]] += 1
    return base + rounded

# Updated generators with minimum allocation
def generate_high_value_stacker(n):
    strats = []
    for _ in range(n):
        weights = np.zeros(NUM_CASTLES)
        weights[6:10] = np.random.dirichlet(np.ones(4))
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['high_value_stacker'] * n

def generate_mid_range_controller(n):
    strats = []
    for _ in range(n):
        weights = np.zeros(NUM_CASTLES)
        weights[3:7] = np.random.dirichlet(np.ones(4))
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['mid_range_controller'] * n

def generate_balanced(n):
    strats = []
    for _ in range(n):
        weights = np.arange(1, NUM_CASTLES + 1) + np.random.uniform(-0.5, 0.5, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['balanced'] * n

def generate_low_castle_attacker(n):
    strats = []
    for _ in range(n):
        weights = np.zeros(NUM_CASTLES)
        weights[0:5] = np.random.dirichlet(np.ones(5))
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['low_castle_attacker'] * n

def generate_reverse_stacker(n):
    strats = []
    for _ in range(n):
        weights = np.linspace(10, 1, NUM_CASTLES) + np.random.normal(0, 1, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['reverse_stacker'] * n

def generate_turtle(n):
    strats = []
    for _ in range(n):
        base = np.full(NUM_CASTLES, TOTAL_SOLDIERS // NUM_CASTLES)
        perturb = np.random.randint(-2, 3, NUM_CASTLES)
        noisy = np.clip(base + perturb, 0, None)
        strats.append(normalize_allocation_with_min(noisy))
    return strats, ['turtle'] * n

# Re-generate the 1500 core strategies
core_strategy_counts = {
    'high_value_stacker': 250,
    'mid_range_controller': 250,
    'balanced': 250,
    'low_castle_attacker': 250,
    'reverse_stacker': 250,
    'turtle': 250
}

all_strats = []
all_names = []
all_types = []

generators = {
    'high_value_stacker': generate_high_value_stacker,
    'mid_range_controller': generate_mid_range_controller,
    'balanced': generate_balanced,
    'low_castle_attacker': generate_low_castle_attacker,
    'reverse_stacker': generate_reverse_stacker,
    'turtle': generate_turtle
}

for strat_type, count in core_strategy_counts.items():
    strat_list, labels = generators[strat_type](count)
    for i, strat in enumerate(strat_list):
        all_strats.append(strat)
        all_names.append(f"{strat_type}_{i+1}")
        all_types.append(strat_type)

# Convert to DataFrame and save
df_core = pd.DataFrame(all_strats, columns=[f"C{i+1}" for i in range(NUM_CASTLES)])
df_core['name'] = all_names
df_core['type'] = all_types


# Streak-focused strategy generators with min 2 per castle

def generate_anti_streak_blocker(n):
    strats = []
    for _ in range(n):
        weights = np.ones(NUM_CASTLES)
        for i in range(0, NUM_CASTLES - 2):
            weights[i:i+3] += np.random.uniform(0, 1.5)  # contest every 3-castle segment
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['anti_streak_blocker'] * n

def generate_3_strike_hunter(n):
    strats = []
    for _ in range(n):
        start = np.random.randint(0, NUM_CASTLES - 2)
        weights = np.ones(NUM_CASTLES)
        weights[start:start+3] += np.random.uniform(3, 6, size=3)  # load specific triple
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['three_strike_hunter'] * n

def generate_streak_breaker(n):
    strats = []
    for _ in range(n):
        weights = np.random.uniform(1, 2, NUM_CASTLES)
        weights[2::3] += 2  # castles 3, 6, 9...
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['streak_breaker'] * n

def generate_early_castle_blitz(n):
    strats = []
    for _ in range(n):
        weights = np.zeros(NUM_CASTLES)
        weights[0:3] = np.random.dirichlet(np.ones(3)) * 2  # triple early stack
        weights += np.random.uniform(0.5, 1.5, NUM_CASTLES)  # some background spread
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['early_castle_blitz'] * n

# Define count per strategy
streak_strategy_counts = {
    'anti_streak_blocker': 350,
    'three_strike_hunter': 350,
    'streak_breaker': 300,
    'early_castle_blitz': 300
}

# Generator mapping
streak_generators = {
    'anti_streak_blocker': generate_anti_streak_blocker,
    'three_strike_hunter': generate_3_strike_hunter,
    'streak_breaker': generate_streak_breaker,
    'early_castle_blitz': generate_early_castle_blitz
}

# Generate
streak_strats = []
streak_names = []
streak_types = []

for strat_type, count in streak_strategy_counts.items():
    strat_list, labels = streak_generators[strat_type](count)
    for i, strat in enumerate(strat_list):
        streak_strats.append(strat)
        streak_names.append(f"{strat_type}_{i+1}")
        streak_types.append(strat_type)

# Save to DataFrame
df_streak = pd.DataFrame(streak_strats, columns=[f"C{i+1}" for i in range(NUM_CASTLES)])
df_streak['name'] = streak_names
df_streak['type'] = streak_types


import random

# === Psychological & Deceptive Strategy Generators ===

def generate_spike_distraction(n):
    strats = []
    for _ in range(n):
        spike = np.random.randint(0, NUM_CASTLES)
        weights = np.random.uniform(1, 2, NUM_CASTLES)
        weights[spike] += np.random.uniform(10, 20)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['spike_distraction'] * n

def generate_mirror_baiter(n):
    strats = []
    for _ in range(n):
        weights = np.ones(NUM_CASTLES)
        if np.random.rand() < 0.5:
            weights[::2] += np.random.uniform(1, 3, len(weights[::2]))  # even castles
        else:
            weights[1::2] += np.random.uniform(1, 3, len(weights[1::2]))  # odd castles
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['mirror_baiter'] * n

def generate_decoy_gambit(n):
    strats = []
    for _ in range(n):
        weights = np.random.uniform(1, 2, NUM_CASTLES)
        high = np.argmax(weights)
        weights[high] *= 0.95  # slightly under-invest in the most tempting castle
        weights += np.random.uniform(0.5, 1, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['decoy_gambit'] * n

# deceptive strategy counts
deceptive_strategy_counts = {
    'spike_distraction': 250,
    'mirror_baiter': 250,
    'decoy_gambit': 200
}

deceptive_generators = {
    'spike_distraction': generate_spike_distraction,
    'mirror_baiter': generate_mirror_baiter,
    'decoy_gambit': generate_decoy_gambit
}

deceptive_strats, deceptive_names, deceptive_types = [], [], []
for strat_type, count in deceptive_strategy_counts.items():
    strat_list, labels = deceptive_generators[strat_type](count)
    for i, strat in enumerate(strat_list):
        deceptive_strats.append(strat)
        deceptive_names.append(f"{strat_type}_{i+1}")
        deceptive_types.append(strat_type)

df_deceptive = pd.DataFrame(deceptive_strats, columns=[f"C{i+1}" for i in range(NUM_CASTLES)])
df_deceptive['name'] = deceptive_names
df_deceptive['type'] = deceptive_types

# === Random Strategy Generator ===

random_name_pool = [
    "chaotic_pigeon", "confused_duck", "lucky_toaster", "noisy_pickle", "clueless_blob",
    "wobbly_melon", "jelly_sword", "forgotten_spoon", "sneaky_grape", "fuzzy_triangle",
    "zigzag_lizard", "unicorn_dust", "tired_shark", "spinning_hat", "wandering_cactus",
    "lonely_penguin", "shrinking_sun", "paranoid_fish", "quantum_fork", "leftover_muffin",
    "slippery_egg", "banana_shadow", "hollow_cheese", "rattling_canoe", "phantom_carrot",
    "spaghetti_hammer", "inverted_umbrella", "chattering_walrus", "digital_doughnut", "vacuum_salmon",
    "fractured_chair", "singing_thermometer", "burnt_ravioli", "enchanted_ladder", "grumpy_cloud",
    "ticklish_paperclip", "melting_icecube", "loose_kite", "secret_baguette", "detached_tentacle",
    "bouncing_snail", "echoing_crayon", "nostalgic_monkey", "fragmented_trombone", "blinking_fruit",
    "rusty_alarm", "compressed_mango", "looping_ostrich", "delirious_banana", "floating_compass"
]

def generate_random_named_strats(n):
    strats = []
    names = []
    types = []
    for i in range(n):
        weights = np.random.rand(NUM_CASTLES)
        strat = normalize_allocation_with_min(weights)
        strats.append(strat)
        name = f"{random.choice(random_name_pool)}_{i+1}"
        names.append(name)
        types.append("random")
    return strats, names, types

random_strats, random_names, random_types = generate_random_named_strats(5550)
df_random = pd.DataFrame(random_strats, columns=[f"C{i+1}" for i in range(NUM_CASTLES)])
df_random['name'] = random_names
df_random['type'] = random_types

# Implement remaining deception + dynamic/adaptive strategies

def generate_trojan_horse(n):
    strats = []
    for _ in range(n):
        zero_castle = np.random.randint(7, 10)  # likely to decoy castle 10, 9, or 8
        weights = np.random.uniform(1, 2, NUM_CASTLES)
        weights[zero_castle] = 0
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['trojan_horse'] * n

def generate_value_thief(n):
    strats = []
    for _ in range(n):
        weights = np.random.uniform(1, 2, NUM_CASTLES)
        top_castle = NUM_CASTLES - 1
        weights[top_castle] *= 0.9 + np.random.uniform(-0.05, 0.05)  # target tie near-castle 10
        weights += np.random.uniform(0.5, 1.5, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['value_thief'] * n

def generate_min_force_dominator(n):
    strats = []
    for _ in range(n):
        weights = 1 / (np.arange(1, NUM_CASTLES + 1)) + np.random.uniform(0, 0.2, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['min_force_dominator'] * n

def generate_point_denial_specialist(n):
    strats = []
    for _ in range(n):
        weights = np.ones(NUM_CASTLES)
        weights[-3:] += np.random.uniform(1, 3, 3)  # castles 8–10
        weights += np.random.uniform(0, 1, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['point_denial_specialist'] * n

def generate_strategic_sacrifice(n):
    strats = []
    for _ in range(n):
        weights = np.random.uniform(1, 2, NUM_CASTLES)
        skip = np.random.choice(range(NUM_CASTLES), size=2, replace=False)
        weights[skip] = 0
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['strategic_sacrifice'] * n

def generate_wave_strategist(n):
    strats = []
    for _ in range(n):
        x = np.linspace(0, 2 * np.pi, NUM_CASTLES)
        weights = (np.sin(x) + 1.2) + np.random.uniform(0, 0.3, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['wave_strategist'] * n

def generate_domino_player(n):
    strats = []
    for _ in range(n):
        weights = np.zeros(NUM_CASTLES)
        pairs = [(0,1), (3,4), (6,7)]
        chosen = random.choice(pairs)
        weights[chosen[0]] = np.random.uniform(1, 3)
        weights[chosen[1]] = np.random.uniform(1, 3)
        weights += np.random.uniform(0.5, 1.5, NUM_CASTLES)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['domino_player'] * n

def generate_nuclear_option(n):
    strats = []
    for _ in range(n):
        full = np.zeros(NUM_CASTLES)
        target = np.random.randint(1, 9)  # avoid extremes
        full[target] = TOTAL_SOLDIERS
        full = np.clip(full, BASELINE_MIN, TOTAL_SOLDIERS)
        strats.append(normalize_allocation_with_min(full))
    return strats, ['nuclear_option'] * n

def generate_chaos_agent(n):
    strats = []
    for _ in range(n):
        weights = np.random.uniform(0.1, 1, NUM_CASTLES)
        weights[0] += np.random.uniform(1, 3)
        weights[4] += np.random.uniform(1, 3)
        weights[9] += np.random.uniform(1, 3)
        strats.append(normalize_allocation_with_min(weights))
    return strats, ['chaos_agent'] * n

# define counts
additional_strategy_counts = {
    'trojan_horse': 100,
    'value_thief': 100,
    'min_force_dominator': 100,
    'point_denial_specialist': 100,
    'strategic_sacrifice': 100,
    'wave_strategist': 100,
    'domino_player': 100,
    'nuclear_option': 100,
    'chaos_agent': 100
}

# generator mapping
additional_generators = {
    'trojan_horse': generate_trojan_horse,
    'value_thief': generate_value_thief,
    'min_force_dominator': generate_min_force_dominator,
    'point_denial_specialist': generate_point_denial_specialist,
    'strategic_sacrifice': generate_strategic_sacrifice,
    'wave_strategist': generate_wave_strategist,
    'domino_player': generate_domino_player,
    'nuclear_option': generate_nuclear_option,
    'chaos_agent': generate_chaos_agent
}

# generate and save
final_strats, final_names, final_types = [], [], []
for strat_type, count in additional_strategy_counts.items():
    strat_list, labels = additional_generators[strat_type](count)
    for i, strat in enumerate(strat_list):
        final_strats.append(strat)
        final_names.append(f"{strat_type}_{i+1}")
        final_types.append(strat_type)

df_final = pd.DataFrame(final_strats, columns=[f"C{i+1}" for i in range(NUM_CASTLES)])
df_final['name'] = final_names
df_final['type'] = final_types


df_all = pd.concat([df_core, df_streak, df_deceptive, df_final, df_random], ignore_index=True)
df_all.to_csv("strategy_pool_full_min2.csv", index=False)
df_all.head()
