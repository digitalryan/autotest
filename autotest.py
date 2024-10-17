import streamlit as st
import pandas as pd
import io
import time
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import Timeout, RequestException

# Streamlit App Title
st.title("Zowie Gen AI Autotesting Tool")

# Initialize session state for DataFrame and time tracking
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Error log function
def log_error(error_message):
    with open('error_log.txt', 'a') as f:
        f.write(f"{time.ctime()}: {error_message}\n")

# Function to call the API with retry logic
def call_api_with_retry(question, retries=3):
    api_url = "https://mock-api.com/answer"  # Replace with actual API endpoint
    for attempt in range(retries):
        try:
            response = requests.post(api_url, json={"question": question}, timeout=5)
            response.raise_for_status()
            return response.json().get('answer', 'No answer available')
        except (Timeout, RequestException) as e:
            log_error(f"Error calling API: {str(e)} (Attempt {attempt + 1})")
            if attempt == retries - 1:
                return "Error fetching answer"
            time.sleep(2)  # Retry delay
    return "No answer available"

# Function to reset the session state without using st.experimental_rerun
def reset_app():
    st.session_state.clear()
    st.write("App has been reset. Please upload a new file or refresh the page to continue.")

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

            try:
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

                    # Create a placeholder to keep the progress information on one line
                    progress_placeholder = st.empty()
                    progress_bar = st.progress(0)

                    # Batch processing using concurrency
                    total_questions = len(df)
                    with ThreadPoolExecutor() as executor:
                        future_to_question = {executor.submit(call_api_with_retry, row['question']): row for index, row in df.iterrows()}

                        for index, future in enumerate(as_completed(future_to_question)):
                            question_row = future_to_question[future]
                            try:
                                # Get the result from the future (answer)
                                answer = future.result()
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
                                progress_placeholder.write(f"Progress: {progress*100:.1f}% - Estimated Time Remaining: {remaining_time:.1f} seconds", unsafe_allow_html=True)

                            except Exception as e:
                                st.error(f"Error processing question: {question_row['question']}")
                                log_error(f"Error processing question: {str(e)}")

                    # Add new columns to the DataFrame
                    df["answer"] = answers
                    df["is_answered"] = is_answered
                    df["explanation"] = explanations

                    # Store the processed DataFrame in session state
                    st.session_state.processed_df = df

            except pd.errors.EmptyDataError:
                st.error("Error reading the file. The file appears to be empty or not valid.")
                log_error("EmptyDataError: The uploaded file is empty or malformed.")

    if st.session_state.processed_df is not None:
        # Display the processed DataFrame from session state
        st.write("Updated CSV with Answers and LLM Evaluation:")
        st.dataframe(st.session_state.processed_df)

        # Save the DataFrame to a buffer for download
        csv_buffer = io.StringIO()
        st.session_state.processed_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Provide a download button with the unique filename
        st.download_button(
            label="Download Test Results",
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

        # Start over with a new file
        if col2.button("Start Over"):
            reset_app()