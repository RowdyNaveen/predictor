import streamlit as st
import requests

# -----------------------------
# Helper Functions
# -----------------------------

def update_transition_matrix(sequence):
    """Calculate transition probabilities from the outcome sequence."""
    counts = {'A': {'A': 0, 'B': 0}, 'B': {'A': 0, 'B': 0}}
    for i in range(1, len(sequence)):
        prev, curr = sequence[i - 1], sequence[i]
        counts[prev][curr] += 1
    matrix = {}
    for state in counts:
        total = counts[state]['A'] + counts[state]['B']
        if total == 0:
            matrix[state] = {'A': 0.5, 'B': 0.5}
        else:
            matrix[state] = {
                'A': counts[state]['A'] / total,
                'B': counts[state]['B'] / total
            }
    return matrix

def get_latest_result(url):
    """
    Fetch the latest game result from the given URL.
    Adjust the data extraction logic based on the actual JSON structure.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Adjust this based on the JSON you receive.
        outcome = data.get('result', None)
        return outcome
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# -----------------------------
# Initialize Session State
# -----------------------------
if 'current_sequence' not in st.session_state:
    st.session_state.current_sequence = []
if 'transition_matrix' not in st.session_state:
    st.session_state.transition_matrix = {
        'A': {'A': 0.5, 'B': 0.5},
        'B': {'A': 0.5, 'B': 0.5}
    }

# -----------------------------
# App Interface
# -----------------------------
st.title("Live Predictor for Fairplay.live")

# Replace this URL with your target URL
url = "https://www.fairplay.live/dc/gamev1.1/teenpatti-one-day-MTUwMDA5-TUFDODgtWDFUUDEwMQ==-TUFDODg=-TWFjODggR2FtaW5n-TUFDSFVC"

if st.button("Fetch Latest Result"):
    latest = get_latest_result(url)
    if latest in ['A', 'B']:
        # Update only if the result is new
        if not st.session_state.current_sequence or st.session_state.current_sequence[-1] != latest:
            st.session_state.current_sequence.append(latest)
            st.session_state.transition_matrix = update_transition_matrix(st.session_state.current_sequence)
            st.success(f"New result: {latest} added!")
        else:
            st.info("Result unchanged from last fetch.")
    else:
        st.warning("No valid result fetched.")

st.write("### Current Sequence of Results")
st.write(st.session_state.current_sequence)

st.write("### Transition Matrix")
st.write(st.session_state.transition_matrix)

# -----------------------------
# Make and Display a Prediction
# -----------------------------
if st.session_state.current_sequence:
    last_state = st.session_state.current_sequence[-1]
    probs = st.session_state.transition_matrix.get(last_state, {'A': 0.5, 'B': 0.5})
    predicted_next = max(probs, key=probs.get)
    st.write(f"**Based on the last result ({last_state}), the predicted next outcome is: {predicted_next}**")
    st.write(f"Probability: {probs[predicted_next]:.2f}")
else:
    st.info("No results available yet for making a prediction.")
