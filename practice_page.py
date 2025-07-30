import streamlit as st
import numpy as np
import pandas as pd
from match_utils import play_full_match, NUM_CASTLES

@st.cache_data
def load_strategy_pool():
    df = pd.read_csv("strategy_pool_full_min2.csv")
    strat_array = df[[f"C{i}" for i in range(1, 11)]].values
    names = df["name"].values
    return strat_array, names

strategy_pool, strategy_names = load_strategy_pool()
CASTLE_VALUES = np.arange(1, NUM_CASTLES + 1)

def practice_mode():
    st.title("🎯 Practice Against the Strategy Pool")
    st.markdown("Enter your own strategy and see how it performs against 10,000 opponents!")

    user_input = st.text_input(
        "Enter your strategy as 10 comma-separated integers that sum to 100:",
        value=st.session_state.get("user_input", "")
    )

    if user_input:
        try:
            user_strategy = np.array([int(x.strip()) for x in user_input.split(',')])
            if len(user_strategy) != 10:
                st.error("Your strategy must have exactly 10 numbers.")
            elif user_strategy.sum() != 100:
                st.error(f"Your strategy sums to {user_strategy.sum()}, but it must sum to 100.")
            elif np.any(user_strategy < 0):
                st.error("All numbers must be non-negative.")
            else:
                st.session_state.user_input = user_input
                st.success("Valid strategy submitted. Evaluating...")

                def apply_3strike(you, them):
                    y_score = t_score = streak_y = streak_t = 0
                    for i in range(NUM_CASTLES):
                        if you[i] > them[i]:
                            y_score += CASTLE_VALUES[i]
                            streak_y += 1
                            streak_t = 0
                        elif them[i] > you[i]:
                            t_score += CASTLE_VALUES[i]
                            streak_t += 1
                            streak_y = 0
                        else:
                            streak_y = streak_t = 0
                        if streak_y == 3:
                            y_score += CASTLE_VALUES[i+1:].sum()
                            break
                        if streak_t == 3:
                            t_score += CASTLE_VALUES[i+1:].sum()
                            break
                    return y_score, t_score

                scores = np.array([apply_3strike(user_strategy, opp) for opp in strategy_pool])
                user_total = scores[:, 0]
                oppo_total = scores[:, 1]

                wins = user_total > oppo_total
                losses = user_total < oppo_total
                draws = user_total == oppo_total

                st.markdown(f"✅ **Wins:** {wins.sum()} / {len(strategy_pool)}")
                st.markdown(f"❌ **Losses:** {losses.sum()} / {len(strategy_pool)}")
                st.markdown(f"➖ **Draws:** {draws.sum()} / {len(strategy_pool)}")

                if losses.sum() > 0:
                    st.markdown("### 😓 Sample Strategies You Lost Against:")

                    loss_indices = np.where(losses)[0]

                    if "sample_losses" not in st.session_state:
                        st.session_state.sample_losses = np.random.choice(
                            loss_indices, size=min(5, len(loss_indices)), replace=False
                        )

                    if st.button("🔁 Show New Loss Examples"):
                        st.session_state.user_input = user_input  # re-store to allow rerun
                        st.session_state.sample_losses = np.random.choice(
                            loss_indices, size=min(5, len(loss_indices)), replace=False
                        )
                        st.rerun()

                    sample_losses = st.session_state.sample_losses
                    true_loss_mask = user_total[sample_losses] < oppo_total[sample_losses]
                    filtered_losses = np.array(sample_losses)[true_loss_mask]

                    if len(filtered_losses) == 0:
                        st.warning("All samples turned out to be ties or wins. Try reloading.")
                    else:
                        df = pd.DataFrame(strategy_pool[filtered_losses], columns=[f"C{i+1}" for i in range(NUM_CASTLES)])
                        df.insert(0, "Strategy Name", strategy_names[filtered_losses])
                        df["Opponent Score"] = oppo_total[filtered_losses]
                        df["Your Score"] = user_total[filtered_losses]
                        st.dataframe(df)

                        st.markdown("---")
                        st.subheader("🔁 Replay a Lost Match with Animation")

                        replay_idx = st.selectbox(
                            "Choose a match to replay:",
                            list(range(len(filtered_losses))),
                            format_func=lambda i: strategy_names[filtered_losses[i]]
                        )

                        if st.button("Replay Match"):
                            play_full_match(
                                user_strategy,
                                strategy_pool[filtered_losses[replay_idx]],
                                p1="You",
                                p2=strategy_names[filtered_losses[replay_idx]]
                            )

        except ValueError:
            st.error("Invalid input. Please enter only comma-separated integers.")
