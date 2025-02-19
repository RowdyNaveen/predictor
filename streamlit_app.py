import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Match Outcome Pattern Analysis")

st.write("""
This app analyzes match outcomes from a CSV file and displays various patterns:
- **Overall win counts and percentages** for each player.
- **Transition matrix** showing the probability of one outcome following another.
- **Streak analysis:** consecutive wins (streaks) for each player.
- **Histogram:** distribution of streak lengths.
- **Other pattern counts:** such as how often outcomes alternate.
""")

# File uploader for CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the CSV file. Adjust delimiter if needed.
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
    else:
        # Verify that the required column exists
        if "result" not in df.columns:
            st.error("The CSV file must contain a column named 'result'.")
        else:
            # Map "Player A" and "Player B" to "A" and "B"
            df["result"] = df["result"].replace({"Player A": "A", "Player B": "B"})
            outcomes = df["result"].tolist()

            st.write("### Raw Data Preview")
            st.dataframe(df.head())

            # Overall statistics
            total_matches = len(outcomes)
            count_A = outcomes.count("A")
            count_B = outcomes.count("B")
            st.write("### Overall Match Outcomes")
            st.write(f"Total matches: **{total_matches}**")
            st.write(f"Player A wins: **{count_A}** ({count_A / total_matches * 100:.2f}%)")
            st.write(f"Player B wins: **{count_B}** ({count_B / total_matches * 100:.2f}%)")

            # --- Transition Matrix Calculation ---
            def update_transition_matrix(sequence):
                counts = {'A': {'A': 0, 'B': 0}, 'B': {'A': 0, 'B': 0}}
                # Count transitions between consecutive outcomes
                for i in range(1, len(sequence)):
                    prev, curr = sequence[i - 1], sequence[i]
                    counts[prev][curr] += 1
                # Convert counts to probabilities
                matrix = {}
                for state in counts:
                    total_state = counts[state]['A'] + counts[state]['B']
                    if total_state == 0:
                        matrix[state] = {'A': 0.5, 'B': 0.5}
                    else:
                        matrix[state] = {
                            'A': counts[state]['A'] / total_state,
                            'B': counts[state]['B'] / total_state
                        }
                return matrix

            transition_matrix = update_transition_matrix(outcomes)
            st.write("### Transition Matrix")
            st.write(transition_matrix)

            # --- Streak Analysis ---
            def compute_streaks(seq):
                """Return a list of tuples: (outcome, streak_length) for consecutive wins."""
                streaks = []
                if not seq:
                    return streaks
                current = seq[0]
                count = 1
                for outcome in seq[1:]:
                    if outcome == current:
                        count += 1
                    else:
                        streaks.append((current, count))
                        current = outcome
                        count = 1
                streaks.append((current, count))
                return streaks

            streaks = compute_streaks(outcomes)
            st.write("### Streak Analysis")
            st.write("List of streaks (Outcome, Length):")
            st.write(streaks)

            # Longest streak for each player
            longest_A = max([s[1] for s in streaks if s[0] == 'A'], default=0)
            longest_B = max([s[1] for s in streaks if s[0] == 'B'], default=0)
            st.write(f"Longest streak for Player A: **{longest_A}**")
            st.write(f"Longest streak for Player B: **{longest_B}**")

            # --- Plotting Streak Lengths ---
            streak_lengths_A = [s[1] for s in streaks if s[0] == 'A']
            streak_lengths_B = [s[1] for s in streaks if s[0] == 'B']

            fig, ax = plt.subplots()
            # Define bins for histogram based on max streak length observed
            max_streak = max(max(streak_lengths_A, default=0), max(streak_lengths_B, default=0))
            bins = np.arange(1, max_streak + 2) - 0.5

            ax.hist(streak_lengths_A, bins=bins, alpha=0.5, label='Player A', color='blue')
            ax.hist(streak_lengths_B, bins=bins, alpha=0.5, label='Player B', color='red')
            ax.set_xlabel("Streak Length")
            ax.set_ylabel("Frequency")
            ax.set_title("Histogram of Streak Lengths")
            ax.legend()
            st.pyplot(fig)

            # --- Other Pattern Analysis ---
            # Count transitions (e.g., A->A, A->B, etc.) using the transition matrix counts
            pattern_counts = {}
            for prev in ['A', 'B']:
                for curr in ['A', 'B']:
                    # Multiply probability by total transitions from 'prev' for an estimate
                    total_prev = outcomes[:-1].count(prev)
                    count = transition_matrix[prev][curr] * total_prev if total_prev > 0 else 0
                    pattern_counts[f"{prev} -> {curr}"] = int(round(count))
            st.write("### Estimated Transition Counts")
            st.write(pattern_counts)

            # Count how often outcomes alternate (i.e., a change from A to B or B to A)
            alternations = sum(1 for i in range(1, len(outcomes)) if outcomes[i] != outcomes[i - 1])
            st.write(f"Number of alternations (changes in outcome): **{alternations}**")
