import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time

NUM_CASTLES = 10
CASTLE_VALUES = list(range(1, 11))

def animated_soldier_clash_charging(blue_count, red_count, frame_delay=0.2):
    container = st.empty()
    i = 0
    while blue_count - i > 0 and red_count - i > 0:
        b_left = max(blue_count - i, 0)
        r_left = max(red_count - i, 0)

        left_pad = "&nbsp;" * (i * 2)
        right_pad = "&nbsp;" * (i * 2)

        blue_soldiers = "🟦" * b_left
        red_soldiers = "🟥" * r_left
        clash_symbol = "⚔️" if b_left > 0 and r_left > 0 else ""

        html = f"""
        <div style='font-size: 30px; font-family: monospace; line-height: 1.2'>
            <div>{left_pad}{blue_soldiers} {clash_symbol} {red_soldiers}{right_pad}</div>
        </div>
        """
        container.markdown(html, unsafe_allow_html=True)
        i += 1
        time.sleep(frame_delay)

    # Final outcome display
    remaining = abs(blue_count - red_count)
    if blue_count > red_count:
        html = f"<div style='text-align: left; font-size: 28px'>🟦 × {remaining}</div>"
    elif red_count > blue_count:
        html = f"<div style='text-align: right; font-size: 28px'>🟥 × {remaining}</div>"
    else:
        html = "<div style='text-align: center; font-size: 28px'>💥 All soldiers fell!</div>"


    container.markdown(html, unsafe_allow_html=True)
    time.sleep(0.5)


def play_full_match(s1, s2, p1="Player 1", p2="Player 2"):
    state = {
        'p1': p1, 'p2': p2,
        's1': s1, 's2': s2,
        'current': 0,
        'score1': 0, 'score2': 0,
        'consec1': 0, 'consec2': 0,
        'log': [],
        'ended': False
    }

    st.subheader(f"Match: {p1} vs {p2}")
    while state['current'] < NUM_CASTLES and not state['ended']:
        i = state['current']
        a, b = s1[i], s2[i]
        result = ""

        if a > b:
            state['score1'] += CASTLE_VALUES[i]
            state['consec1'] += 1
            state['consec2'] = 0
            result = f"{p1} wins castle {i+1} ({CASTLE_VALUES[i]} pts)"
        elif b > a:
            state['score2'] += CASTLE_VALUES[i]
            state['consec2'] += 1
            state['consec1'] = 0
            result = f"{p2} wins castle {i+1} ({CASTLE_VALUES[i]} pts)"
        else:
            state['consec1'] = state['consec2'] = 0
            result = f"Castle {i+1} is a draw"

        st.markdown(f"## 🏰 Resolving Castle {i + 1} 🏰")
        animated_soldier_clash_charging(a , b)

        if state['consec1'] == 3:
            result += f" — {p1} triggers 3-strike rule!"
            state['score1'] += sum(CASTLE_VALUES[i+1:])
            state['ended'] = True
            _three_strike_flash(p1)

        elif state['consec2'] == 3:
            result += f" — {p2} triggers 3-strike rule!"
            state['score2'] += sum(CASTLE_VALUES[i+1:])
            state['ended'] = True
            _three_strike_flash(p2)

        state['log'].append(result)
        state['current'] += 1
        time.sleep(0.6)

    st.write("### Match Log")
    for entry in state['log']:
        st.write(entry)

    st.success(f"Final Score — {p1}: {state['score1']}, {p2}: {state['score2']}")

    # Bar chart of allocations
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(NUM_CASTLES)
    width = 0.35
    ax.bar(x, s1, width, label=p1, color='blue')
    ax.bar(x + width, s2, width, label=p2, color='red')
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([f"C{i+1}" for i in range(NUM_CASTLES)])
    ax.set_ylabel("Soldiers")
    ax.set_title(f"Allocation: {p1} vs {p2}")
    ax.legend()
    st.pyplot(fig)

    return state['score1'], state['score2']


def _three_strike_flash(player_name):
    st.markdown(f"""
        <div style="font-size: 36px; color: red; text-align: center; animation: flash 1s infinite;">
            ⚡ 3-Strike Triggered by {player_name}! ⚡
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
