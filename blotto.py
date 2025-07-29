import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

NUM_CASTLES = 10
CASTLE_VALUES = list(range(1, 11))
def animated_soldier_clash_charging(blue_count, red_count, frame_delay=0.2):
    container = st.empty()
    frames = max(blue_count, red_count)
    for i in range(frames + 1):
        b_left = max(blue_count - i, 0)
        r_left = max(red_count - i, 0)

        # Indentation increases with i
        left_pad = "&nbsp;" * (i * 2)
        right_pad = "&nbsp;" * (i * 2)

        blue_soldiers = "🟦" * b_left
        red_soldiers = "🟥" * r_left

        # Center line
        clash_symbol = "⚔️" if b_left > 0 and r_left > 0 else ""

        html = f"""
        <div style='font-size: 30px; font-family: monospace; line-height: 1.2'>
            <div>{left_pad}{blue_soldiers} {clash_symbol} {red_soldiers}{right_pad}</div>
        </div>
        """
        container.markdown(html, unsafe_allow_html=True)
        time.sleep(frame_delay)

    # Final result
    if blue_count > red_count:
        survivors = "🟦" * (blue_count - red_count)
        html = f"<div style='text-align: left; font-size: 30px'>{survivors}</div>"
    elif red_count > blue_count:
        survivors = "🟥" * (red_count - blue_count)
        html = f"<div style='text-align: right; font-size: 30px'>{survivors}</div>"
    else:
        html = "<div style='text-align: center; font-size: 30px'>💥 All soldiers fell!</div>"

    container.markdown(html, unsafe_allow_html=True)
    time.sleep(0.5)


# Session state
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'results' not in st.session_state:
    st.session_state.results = []
if 'match_state' not in st.session_state:
    st.session_state.match_state = {}

st.title("Blotto Game Web App")

# Sidebar: switch rounds
if st.sidebar.button("Switch to Round 2"):
    st.session_state.round = 2

st.sidebar.write(f"**Current Round**: {st.session_state.round}")

# Add player form
st.header("Add Player")
with st.form("add_player_form"):
    name = st.text_input("Player name")
    strategy_inputs = []
    num_strat = 1 if st.session_state.round == 1 else 3
    for i in range(num_strat):
        strat = st.text_input(f"Strategy {i+1} (comma-separated 10 numbers)", key=f"{name}_s{i}")
        strategy_inputs.append(strat)
    submitted = st.form_submit_button("Add Player")
    if submitted:
        strategies = []
        for idx, s in enumerate(strategy_inputs):
            try:
                vec = list(map(int, s.split(',')))
            except ValueError:
                st.error(f"Strategy {idx + 1}: Could not parse all values as integers.")
                break

            if len(vec) != 10:
                st.error(f"Strategy {idx + 1}: Must contain exactly 10 values.")
                break

            if sum(vec) != 100:
                st.error(f"Strategy {idx + 1}: Values must sum to 100 (currently {sum(vec)}).")
                break

            if any(x < 0 for x in vec):
                st.error(f"Strategy {idx + 1}: All values must be non-negative.")
                break

            strategies.append(vec)
        else:
            st.session_state.players[name] = strategies
            st.success(f"Added {name} with {num_strat} strategy(ies).")


# Show current players
st.header("Current Players")
for p, strategies in st.session_state.players.items():
    st.write(f"**{p}**: {len(strategies)} strategy(ies)")

# Match simulation
st.header("Play Match")
player_names = list(st.session_state.players.keys())
if len(player_names) >= 2:
    p1 = st.selectbox("Player 1", player_names, key="p1")
    p2 = st.selectbox("Player 2", [x for x in player_names if x != p1], key="p2")

    if st.session_state.round == 1:
        s1 = st.session_state.players[p1][0]
        s2 = st.session_state.players[p2][0]
    else:
        strat1 = st.selectbox(f"Select strategy for {p1}", [1, 2, 3])
        strat2 = st.selectbox(f"Select strategy for {p2}", [1, 2, 3])
        s1 = st.session_state.players[p1][strat1 - 1]
        s2 = st.session_state.players[p2][strat2 - 1]

    if st.button("Start Match"):
        st.session_state.match_state = {
            'p1': p1, 'p2': p2,
            's1': s1, 's2': s2,
            'current': 0,
            'score1': 0, 'score2': 0,
            'consec1': 0, 'consec2': 0,
            'log': [],
            'ended': False
        }

# Match visual + step
# Auto-play full match
if st.session_state.match_state:
    state = st.session_state.match_state
    st.subheader(f"Match: {state['p1']} vs {state['p2']}")
    if not state['ended']:
        while state['current'] < NUM_CASTLES and not state['ended']:
            i = state['current']
            a, b = state['s1'][i], state['s2'][i]
            result = ""
            if a > b:
                state['score1'] += CASTLE_VALUES[i]
                state['consec1'] += 1
                state['consec2'] = 0
                result = f"{state['p1']} wins castle {i+1} ({CASTLE_VALUES[i]} pts)"
            elif b > a:
                state['score2'] += CASTLE_VALUES[i]
                state['consec2'] += 1
                state['consec1'] = 0
                result = f"{state['p2']} wins castle {i+1} ({CASTLE_VALUES[i]} pts)"
            else:
                state['consec1'] = state['consec2'] = 0
                result = f"Castle {i+1} is a draw"

            # Show charging animation
            blue_count = a // 2
            red_count = b // 2
            st.markdown(f"## 🏰 Resolving Castle {i + 1} 🏰")
            animated_soldier_clash_charging(blue_count, red_count)

            if state['consec1'] == 3:
                result += f" — {state['p1']} triggers 3-strike rule!"
                state['score1'] += sum(CASTLE_VALUES[i+1:])
                state['ended'] = True

                st.markdown(f"""
                <div style="font-size: 36px; color: red; text-align: center; animation: flash 1s infinite;">
                    ⚡ 3-Strike Triggered by {state['p1']}! ⚡
                </div>
                <style>
                @keyframes flash {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.1; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)
                time.sleep(1.5)

            elif state['consec2'] == 3:
                result += f" — {state['p2']} triggers 3-strike rule!"
                state['score2'] += sum(CASTLE_VALUES[i+1:])
                state['ended'] = True

                st.markdown(f"""
                <div style="font-size: 36px; color: red; text-align: center; animation: flash 1s infinite;">
                    ⚡ 3-Strike Triggered by {state['p2']}! ⚡
                </div>
                <style>
                @keyframes flash {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.1; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)
                time.sleep(1.5)

            state['log'].append(result)
            state['current'] += 1
            time.sleep(0.6)  # Delay between castles

        state['ended'] = True


    st.write("### Match Log")
    for entry in state['log']:
        st.write(entry)

    if state['ended']:
        st.success(f"Final Score — {state['p1']}: {state['score1']}, {state['p2']}: {state['score2']}")
        st.session_state.results.append({
            "Player 1": state['p1'],
            "Player 2": state['p2'],
            "Score 1": state['score1'],
            "Score 2": state['score2']
        })

        # Visualize soldier bars only after match ends
        fig, ax = plt.subplots(figsize=(10, 4))
        x = np.arange(NUM_CASTLES)
        width = 0.35
        ax.bar(x, state['s1'], width, label=state['p1'], color='blue')
        ax.bar(x + width, state['s2'], width, label=state['p2'], color='red')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels([f"C{i+1}" for i in range(NUM_CASTLES)])
        ax.set_ylabel("Soldiers")
        ax.set_title(f"Allocation: {state['p1']} vs {state['p2']}")
        ax.legend()
        st.pyplot(fig)

        # Clear match state
        st.session_state.match_state = {}


# Show match history
if st.session_state.results:
    st.header("Match History")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)

