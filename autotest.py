import streamlit as st
import pandas as pd
import io
import time
import os

# Streamlit App Title
st.title("CSV Question Answering and Evaluation App")

# Initialize session state for DataFrame
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

# File Upload Interface
uploaded_file = st.file_uploader("Upload a CSV or Excel file with questions", type=["csv", "xlsx"])

if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    try:
        st.write(f"Attempting to read file: {uploaded_file.name}")
        st.write(f"File size: {uploaded_file.size} bytes")
        
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            st.stop()
        
        st.write(f"File read successfully. Shape: {df.shape}")
        
        if df.empty:
            st.error("The uploaded file is empty. Please upload a file with data.")
            st.stop()
    except pd.errors.EmptyDataError:
        st.error("The uploaded file appears to be empty. Please check the file and try again.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the file: {type(e).__name__}")
        st.write("Please check your file and try again.")
        st.stop()

if uploaded_file:
    # Generate a unique filename for the output CSV
    original_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{original_filename}_autotest.csv"

    # If the DataFrame is not already processed, read and process it
    if st.session_state.processed_df is None:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file)

        if "question" not in df.columns:
            st.error("The uploaded file must contain a 'question' column.")
        else:
            # Show the uploaded questions
            st.write("Uploaded Questions:")
            st.dataframe(df)

            # Placeholder for new columns
            answers = []
            is_answered = []
            explanations = []

            st.write("Processing questions...")
            progress_bar = st.progress(0)

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

                # Update progress bar
                progress = (index + 1) / len(df)
                progress_bar.progress(progress)

            # Add new columns to the DataFrame
            df["answer"] = answers
            df["is_answered"] = is_answered
            df["explanation"] = explanations

            # Store the processed DataFrame in session state
            st.session_state.processed_df = df

    # Display the processed DataFrame from session state
    st.write("Updated File with Mock Answers and LLM Evaluation:")
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
