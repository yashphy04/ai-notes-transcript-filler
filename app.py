import streamlit as st
import pandas as pd
from transformers import pipeline
from io import BytesIO

@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

generator = load_model()

def generate_notes(row):
    prompt = f"Summary: {row['Summary']}. Intent: {row['Intent / purpose of the call']}. Sentiment: {row['Sentiment of the customer']}. Vibe: {row['Vibe of the engagement']}."
    try:
        result = generator(prompt, max_length=60, do_sample=True)[0]['generated_text']
    except:
        result = "Could not generate"
    return result

def generate_transcript(row):
    prompt = f"Generate a brief transcript for a mentor-student call. Summary: {row['Summary']}. Intent: {row['Intent / purpose of the call']}. Sentiment: {row['Sentiment of the customer']}."
    try:
        result = generator(prompt, max_length=80, do_sample=True)[0]['generated_text']
    except:
        result = "Could not generate"
    return result

st.title("AI Notes and Transcript Filler")
st.write("Upload your Excel file. AI will fill in missing Notes and Transcripts.")

uploaded_file = st.file_uploader("Choose an Excel file (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    with st.spinner("Generating missing Notes..."):
        df['Notes'] = df.apply(lambda row: generate_notes(row) if pd.isna(row['Notes']) else row['Notes'], axis=1)

    with st.spinner("Generating missing Transcripts..."):
        df['Transcript'] = df.apply(lambda row: generate_transcript(row) if pd.isna(row['Transcript']) else row['Transcript'], axis=1)

    st.success("AI filling complete")
    st.dataframe(df.head())

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button("Download AI-Filled Excel", data=output.getvalue(), file_name="AI_Filled_Output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")