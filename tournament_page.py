import streamlit as st
import pandas as pd
import numpy as np
from match_utils import play_full_match, NUM_CASTLES
from collections import defaultdict

def tournament_mode():
    if 'round' not in st.session_state:
        st.session_state.round = 1
    if 'players' not in st.session_state:
        st.session_state.players = {}
    if 'results_r1' not in st.session_state:
        st.session_state.results_r1 = []
    if 'results_r2' not in st.session_state:
        st.session_state.results_r2 = []

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
        strategy_inputs = [st.text_input(f"Strategy {i+1} (comma-separated 10 numbers)", key=f"strat_input_{i}") for i in range(num_strat)]
        submitted = st.form_submit_button("Add Player")
        if submitted:
            strategies = []
            for idx, s in enumerate(strategy_inputs):
                try:
                    vec = list(map(int, s.split(',')))
                    assert len(vec) == 10 and sum(vec) == 100 and all(x >= 0 for x in vec)
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
            s1, s2 = st.session_state.players[p1][0], st.session_state.players[p2][0]
        else:
            strat1 = st.selectbox(f"Select strategy for {p1}", [1, 2, 3])
            strat2 = st.selectbox(f"Select strategy for {p2}", [1, 2, 3])
            s1 = st.session_state.players[p1][strat1 - 1]
            s2 = st.session_state.players[p2][strat2 - 1]
        if st.button("Start Match"):
            score1, score2 = play_full_match(s1, s2, p1, p2)
            match = {"Player 1": p1, "Player 2": p2, "Score 1": score1, "Score 2": score2}
            if st.session_state.round == 1:
                st.session_state.results_r1.append(match)
            else:
                st.session_state.results_r2.append(match)

    # Match history and scoreboard
    results = st.session_state.results_r1 if st.session_state.round == 1 else st.session_state.results_r2
    st.header("📊 Scoreboard")

    win_counts = defaultdict(int)
    total_points = defaultdict(int)
    for match in results:
        p1, p2 = match["Player 1"], match["Player 2"]
        s1, s2 = match["Score 1"], match["Score 2"]
        total_points[p1] += s1
        total_points[p2] += s2
        if s1 > s2:
            win_counts[p1] += 1
        elif s2 > s1:
            win_counts[p2] += 1

    all_players = list(st.session_state.players.keys())
    if all_players:
        scoreboard = pd.DataFrame([{
            "Player": p,
            "Wins": win_counts[p],
            "Total Score": total_points[p]
        } for p in all_players]).sort_values(by="Wins", ascending=False)
        st.dataframe(scoreboard, use_container_width=True)

        # Head-to-head visual
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        import seaborn as sns

        # Head-to-head visual
        st.subheader("🟢 Head-to-Head Outcomes 🔴")

        outcome_matrix = np.full((len(all_players), len(all_players)), np.nan)

        for i, pi in enumerate(all_players):
            for j, pj in enumerate(all_players):
                if pi == pj:
                    continue
                wins = any(
                    (m["Player 1"] == pi and m["Player 2"] == pj and m["Score 1"] > m["Score 2"]) or
                    (m["Player 2"] == pi and m["Player 1"] == pj and m["Score 2"] > m["Score 1"])
                    for m in results
                )
                losses = any(
                    (m["Player 1"] == pi and m["Player 2"] == pj and m["Score 1"] < m["Score 2"]) or
                    (m["Player 2"] == pi and m["Player 1"] == pj and m["Score 2"] < m["Score 1"])
                    for m in results
                )
                if wins:
                    outcome_matrix[i][j] = 1
                elif losses:
                    outcome_matrix[i][j] = -1
                else:
                    outcome_matrix[i][j] = 0

        cmap = mcolors.ListedColormap(["#ff9999", "white", "#99ff99"])  # red, white, green
        bounds = [-1.5, -0.5, 0.5, 1.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        fig, ax = plt.subplots(figsize=(6, 6))
        sns.heatmap(
            outcome_matrix,
            cmap=cmap,
            norm=norm,
            cbar=False,
            xticklabels=all_players,
            yticklabels=all_players,
            linewidths=0.5,
            linecolor='gray',
            square=True,
            annot=False,
            ax=ax
        )
        ax.set_xlabel("Opponent")
        ax.set_ylabel("Player")
        st.pyplot(fig)

    else:
        st.info("Scoreboard will appear here once players have been added and matches played.")

    # Match history with delete buttons
    st.header("🕹 Match History")
    for i, match in enumerate(results):
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"- **{match['Player 1']}** ({match['Score 1']}) vs **{match['Player 2']}** ({match['Score 2']})")
        with col2:
            if st.button("🗑️", key=f"delete_{st.session_state.round}_{i}"):
                (st.session_state.results_r1 if st.session_state.round == 1 else st.session_state.results_r2).pop(i)
                st.experimental_rerun()
