import streamlit as st
import pandas as pd
import io
import time  # To simulate latency

# Step 1: Streamlit App Title
st.title("Zowie Autotest")

# Step 2: File Upload Interface
uploaded_file = st.file_uploader("Upload a CSV file with questions", type=["csv"])

if uploaded_file:
    # Step 3: Read Uploaded CSV
    df = pd.read_csv(uploaded_file)

    if "question" not in df.columns:
        st.error("The uploaded CSV must contain a 'question' column.")
    else:
        # Optional: Show the uploaded questions
        st.write("Uploaded Questions:")
        st.dataframe(df)

        # Placeholder for the responses
        answers = []

        # Step 4: Mock API response processing (instead of calling a real API)
        st.write("Simulating API calls for the uploaded questions...")

        progress_bar = st.progress(0)  # Progress bar to indicate processing

        for index, row in df.iterrows():
            question = row["question"]

            # Simulate API latency
            time.sleep(1)

            # Mock answer generation (you can change this logic if needed)
            answer = f"Mock answer to: '{question}'"
            answers.append(answer)

            # Update progress bar
            progress = (index + 1) / len(df)
            progress_bar.progress(progress)

        # Step 5: Add answers to the DataFrame
        df["answer"] = answers

        # Display the DataFrame with answers
        st.write("Updated CSV with Mock Answers:")
        st.dataframe(df)

        # Step 6: Allow Download of the Updated CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="Download CSV with Answers",
            data=csv_data,
            file_name="questions_with_mock_answers.csv",
            mime="text/csv",
        )