import streamlit as st
from match_utils import play_full_match, NUM_CASTLES

# Session state defaults
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'results' not in st.session_state:
    st.session_state.results = []

def tournament_mode():
    st.title("🏆 Blotto Tournament")

    # Sidebar
    if st.sidebar.button("Switch to Round 2"):
        st.session_state.round = 2
    st.sidebar.write(f"**Current Round:** {st.session_state.round}")

    # Add player
    st.header("Add Player")
    with st.form("add_player_form"):
        name = st.text_input("Player name")
        num_strat = 1 if st.session_state.round == 1 else 3
        strategy_inputs = []
        for i in range(num_strat):
            strat = st.text_input(f"Strategy {i+1} (comma-separated 10 numbers)", key=f"strat_input_{i}")
            strategy_inputs.append(strat)

        submitted = st.form_submit_button("Add Player")
        if submitted:
            strategies = []
            for idx, s in enumerate(strategy_inputs):
                try:
                    vec = list(map(int, s.split(',')))
                    assert len(vec) == 10
                    assert sum(vec) == 100
                    assert all(x >= 0 for x in vec)
                    strategies.append(vec)
                except:
                    st.error(f"Strategy {idx+1} must be 10 non-negative integers summing to 100.")
                    break
            else:
                st.session_state.players[name] = strategies
                st.success(f"Added {name} with {num_strat} strategy(ies).")

    # Show players
    st.header("Current Players")
    for p, s in st.session_state.players.items():
        st.write(f"**{p}**: {len(s)} strategy(ies)")

    # Match play
    st.header("Play Match")
    players = list(st.session_state.players.keys())
    if len(players) >= 2:
        p1 = st.selectbox("Player 1", players, key="p1_select")
        p2 = st.selectbox("Player 2", [p for p in players if p != p1], key="p2_select")

        if st.session_state.round == 1:
            s1 = st.session_state.players[p1][0]
            s2 = st.session_state.players[p2][0]
        else:
            strat1 = st.selectbox(f"Select strategy for {p1}", [1, 2, 3])
            strat2 = st.selectbox(f"Select strategy for {p2}", [1, 2, 3])
            s1 = st.session_state.players[p1][strat1 - 1]
            s2 = st.session_state.players[p2][strat2 - 1]

        if st.button("Start Match"):
            score1, score2 = play_full_match(s1, s2, p1, p2)
            st.session_state.results.append({
                "Player 1": p1, "Player 2": p2,
                "Score 1": score1, "Score 2": score2
            })

    # Match history
    if st.session_state.results:
        st.header("Match History")
        st.dataframe(st.session_state.results)
