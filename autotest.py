import streamlit as st
import pandas as pd
import io
import time
import os

# Streamlit App Title
st.title("CSV Question Answering and Evaluation App")

# Initialize session state for DataFrame and time tracking
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Function to reset the app
def reset_app():
    st.session_state.processed_df = None
    st.session_state.start_time = None
    st.experimental_rerun()

# File Upload Interface (Only CSV)
uploaded_file = st.file_uploader("Upload a CSV file with questions", type=["csv"])

if uploaded_file:
    # Generate a unique filename for the output CSV
    original_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{original_filename}_autotest.csv"

    # If the DataFrame is not already processed, show the "Run Test" button
    if st.session_state.processed_df is None:
        if st.button("Run Test"):
            st.session_state.start_time = time.time()  # Record start time

            # Process CSV
            df = pd.read_csv(uploaded_file)

            if "question" not in df.columns:
                st.error("The uploaded CSV must contain a 'question' column.")
            else:
                # Show uploaded questions
                st.write("Uploaded Questions:")
                st.dataframe(df)

                # Placeholders for new columns
                answers = []
                is_answered = []
                explanations = []

                st.write("Processing questions...")
                progress_bar = st.progress(0)

                # Create a placeholder to keep the progress information on one line
                progress_placeholder = st.empty()

                total_questions = len(df)
                for index, row in df.iterrows():
                    question = row["question"]

                    # Simulate latency
                    time.sleep(1)

                    # Mock answer generation
                    answer = f"Mock answer to: '{question}'"
                    answers.append(answer)

                    # Mock LLM-based classification
                    mock_is_answered = "Yes" if index % 2 == 0 else "No"
                    mock_explanation = f"Mock explanation for question {index + 1}"

                    is_answered.append(mock_is_answered)
                    explanations.append(mock_explanation)

                    # Calculate progress
                    progress = (index + 1) / total_questions
                    elapsed_time = time.time() - st.session_state.start_time
                    estimated_total_time = (elapsed_time / (index + 1)) * total_questions
                    remaining_time = estimated_total_time - elapsed_time

                    # Update progress bar
                    progress_bar.progress(progress)

                    # Update the same line for progress percentage and time remaining
                    progress_placeholder.write(f"Progress: {progress*100:.2f}% - Estimated Time Remaining: {remaining_time:.1f} seconds", unsafe_allow_html=True)

                # Add new columns to the DataFrame
                df["answer"] = answers
                df["is_answered"] = is_answered
                df["explanation"] = explanations

                # Store the processed DataFrame in session state
                st.session_state.processed_df = df

    if st.session_state.processed_df is not None:
        # Display the processed DataFrame from session state
        st.write("Updated CSV with Mock Answers and LLM Evaluation:")
        st.dataframe(st.session_state.processed_df)

        # Save the DataFrame to a buffer for download
        csv_buffer = io.StringIO()
        st.session_state.processed_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Provide a download button with the unique filename
        st.download_button(
            label="Download CSV with Answers and LLM Evaluation",
            data=csv_data,
            file_name=output_filename,
            mime="text/csv",
        )

        # Add "Re-run" and "Start Over" buttons AFTER test completion
        st.write("---")  # Separator
        st.write("Would you like to run another test or start a new one?")
        
        col1, col2 = st.columns(2)

        # Re-run with the same file
        if col1.button("Re-run Test"):
            st.session_state.processed_df = None
            st.experimental_rerun()
