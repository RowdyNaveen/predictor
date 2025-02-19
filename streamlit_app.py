import streamlit as st
import pandas as pd

def update_transition_matrix(sequence):
    """
    Given a list of match outcomes (e.g., ['A', 'B', 'A', ...]),
    compute the transition probabilities for a first-order Markov chain.
    """
    counts = {'A': {'A': 0, 'B': 0}, 'B': {'A': 0, 'B': 0}}
    # Count transitions between consecutive outcomes
    for i in range(1, len(sequence)):
        prev, curr = sequence[i - 1], sequence[i]
        counts[prev][curr] += 1
    
    # Convert counts to probabilities
    matrix = {}
    for state in counts:
        total = counts[state]['A'] + counts[state]['B']
        if total == 0:
            matrix[state] = {'A': 0.5, 'B': 0.5}  # Default if no data
        else:
            matrix[state] = {
                'A': counts[state]['A'] / total,
                'B': counts[state]['B'] / total
            }
    return matrix

# -----------------------------
# Streamlit App Interface
# -----------------------------
st.title("CSV-based Match Outcome Predictor")

st.write("Upload a CSV file containing your match results. The file should have a column named `result` with values `A` or `B`.")

# File uploader for CSV
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Read CSV file into a DataFrame
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
    else:
        # Check if the CSV has the required 'result' column
        if "result" not in df.columns:
            st.error("The CSV file must contain a column named 'result'.")
        else:
            # Extract match sequence from the 'result' column
            sequence = df["result"].tolist()
            
            # Filter to keep only valid outcomes
            valid_sequence = [x for x in sequence if x in ['A', 'B']]
            if not valid_sequence:
                st.error("No valid match results ('A' or 'B') were found in the CSV file.")
            else:
                # Display the match sequence
                st.write("### Match Sequence")
                st.write(valid_sequence)
                
                # Compute the transition matrix based on the sequence
                transition_matrix = update_transition_matrix(valid_sequence)
                st.write("### Transition Matrix")
                st.write(transition_matrix)
                
                # Make a prediction based on the last match outcome
                last_state = valid_sequence[-1]
                probs = transition_matrix.get(last_state, {'A': 0.5, 'B': 0.5})
                predicted_next = max(probs, key=probs.get)
                
                st.write(f"**Based on the last result ({last_state}), the predicted next outcome is: {predicted_next}**")
                st.write(f"Probability: {probs[predicted_next]:.2f}")
