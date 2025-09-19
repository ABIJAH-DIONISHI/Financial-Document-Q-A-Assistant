import streamlit as st
import pandas as pd
import requests
import pdfplumber  

st.title("📊 Financial QA with Ollama")

uploaded_file = st.file_uploader("Upload PDF or CSV", type=["pdf", "csv"])
doc_text = ""

if uploaded_file is not None:
    try:
        st.success("✅ File uploaded successfully!")
        st.write(f"**File name:** {uploaded_file.name}")
        st.write(f"**File type:** {uploaded_file.type}")
        st.write(f"**File size:** {uploaded_file.size/1024:.2f} KB")

        # Handle CSV
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            st.subheader("📄 Preview of CSV Data")
            st.dataframe(df.head())
            doc_text = df.to_csv(index=False)

        # Handle PDF
        elif uploaded_file.type == "application/pdf":
            doc_text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        doc_text += page_text + "\n"
            st.subheader("📄 Extracted PDF Text")
            if doc_text.strip():
                st.text_area("Extracted Content", doc_text, height=300)
            else:
                st.warning("No extractable text found in this PDF (it may be scanned).")
    except Exception as e:
        st.error(f"❌ An error occurred during file processing: {e}")
        st.info("Please ensure the file format is correct and not corrupted.")
else:
    st.info("Please upload a file to proceed.")

# --- Ask a Question ---
question = st.text_input("Ask a question about this document:")

if st.button("Get Answer"):
    if not doc_text.strip():
        st.warning("Please upload a document first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.2",
            "prompt": f"Document:\n{doc_text}\n\nQuestion: {question}",
            "stream": False
        }
        try:
            resp = requests.post(url, json=payload, timeout=60)
            data = resp.json()
            answer = data.get("response", "")
            st.subheader("Answer:")
            st.write(answer)
        except Exception as e:
            st.error(f"Error contacting Ollama: {e}")
            st.info("Is Ollama running? Try: `ollama pull llama3.2` and `ollama serve`.")
