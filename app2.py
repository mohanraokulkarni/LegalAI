import PyPDF2
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer, util
import spacy
import streamlit as st
import os
from PyPDF2 import PdfReader
import numpy as np
import base64


# Step 1: Read and Extract Text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# Step 2: Summarize the PDF Content
def summarize_text(text):
    summarizer = pipeline("summarization", model="t5-small")  # Smaller model for faster performance
    max_chunk_size = 2048  # Larger chunks reduce the number of iterations
    text_chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    # Summarize each chunk
    summaries = []
    for chunk in text_chunks:
        summaries.append(
            summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        )

    summarized_text = " ".join(summaries)
    return summarized_text


# Step 3: Advanced Question-Answering
def advanced_question_answering(question, text):
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
    result = qa_pipeline(question=question, context=text)
    return result['answer']


# Step 4: Behavioral Manipulation Detection
def detect_behavioral_manipulation(text):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Categories for manipulation
    flagged_issues = {}

    # Risk levels for manipulative language
    risk_mapping = {
        "Overcomplex sentence": "Medium",
        "Ambiguity detected": "Low",
        "Unfair clause detected": "High",
        "Vague language detected": "Medium",
        "Negative sentiment detected": "High"
    }

    for sentence in doc.sents:
        sentence_issues = []

        # 1. Detect Overcomplexity (Medium Risk)
        if len(sentence) > 30:
            sentence_issues.append("Overcomplex sentence")

        # 2. Detect Ambiguity (Low Risk)
        ambiguous_words = ["may", "might", "could", "possibly", "at discretion", "subject to"]
        if any(word in sentence.text.lower() for word in ambiguous_words):
            sentence_issues.append("Ambiguity detected")

        # 3. Detect Unbalanced or Unfair Clauses (High Risk)
        unfair_phrases = ["binding arbitration", "non-compete", "without notice", "sole discretion", "irrevocable"]
        if any(phrase in sentence.text.lower() for phrase in unfair_phrases):
            sentence_issues.append("Unfair clause detected")

        # 4. Detect Vagueness or Lack of Specificity (Medium Risk)
        vague_phrases = ["as necessary", "at any time", "as deemed necessary", "without limitation"]
        if any(phrase in sentence.text.lower() for phrase in vague_phrases):
            sentence_issues.append("Vague language detected")

        # 5. Detect Negative Sentiment (High Risk)
        sentiment_words = ["terminate", "penalty", "liable", "breach"]
        if any(word in sentence.text.lower() for word in sentiment_words):
            sentence_issues.append("Negative sentiment detected")

        # Add flagged issues with risk levels (only High Risk)
        for issue in sentence_issues:
            if risk_mapping[issue] == "High":  # Only consider High-risk issues
                flagged_issues[sentence.text.strip()] = f"{issue} (Risk: High)"

    return flagged_issues



# Step 5: Dynamic Sentiment and Emotion Analysis
def sentiment_emotion_analysis(text):
    emotion_analyzer = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion")
    emotions = emotion_analyzer(text, truncation=True, max_length=512)

    # Group and analyze all emotions detected
    emotion_summary = {}
    for emotion in emotions:
        label = emotion['label']
        score = emotion['score']
        if label in emotion_summary:
            emotion_summary[label] += score
        else:
            emotion_summary[label] = score

    # Sort and return the emotions
    sorted_emotions = sorted(emotion_summary.items(), key=lambda x: x[1], reverse=True)
    return sorted_emotions


# Suggestions Without API
def generate_dynamic_suggestions(flagged_clauses, full_text):
    """
    Generate dynamic suggestions based on the flagged manipulative clauses and the context of the PDF document.

    Parameters:
    - flagged_clauses (dict): Dictionary where keys are manipulative sentences and values are their types and risk levels.
    - full_text (str): Full text of the PDF document for context.

    Returns:
    - List of suggestions dynamically tailored to each clause.
    """
    suggestions = []

    for clause, issue in flagged_clauses.items():
        suggestion = f""

        # Tailored suggestions based on the detected issue
        if "Unfair clause detected" in issue:
            suggestion += (
                "Suggestion: Revise this clause to include mutual agreement terms or involve third-party mediation. "
                "For example, replace 'sole discretion' with 'upon mutual agreement.'"
            )

        elif "Negative sentiment detected" in issue:
            suggestion += (
                "Suggestion: Rephrase this clause to reduce negative connotations. "
                "Consider using neutral language, such as replacing 'terminate without notice' with 'terminate with prior written notice.'"
            )

        elif "Overcomplex sentence" in issue:
            suggestion += (
                "Suggestion: Simplify this clause for better readability. Break it into shorter sentences, and use bullet points if applicable."
            )

        elif "Vague language detected" in issue:
            suggestion += (
                "Suggestion: Add specific details to clarify vague terms. For instance, replace 'as necessary' with "
                "'as necessary, no later than 30 days from the issue date.'"
            )

        elif "Ambiguity detected" in issue:
            suggestion += (
                "Suggestion: Define ambiguous terms clearly. Replace words like 'may' or 'subject to' with definitive statements, "
                "e.g., 'will require approval from both parties within 14 days.'"
            )

        # Context-specific dynamic advice
        if "termination" in clause.lower():
            suggestion += (
                " Ensure termination conditions are explicitly outlined to avoid ambiguity, such as specifying notice periods or conditions."
            )

        if "confidentiality" in full_text.lower() and "never disclose" in clause.lower():
            suggestion += (
                " Suggestion: Limit confidentiality obligations to a reasonable timeframe (e.g., 1-3 years) after termination."
            )

        if "non-compete" in full_text.lower() and "5 years" in clause.lower():
            suggestion += (
                " Suggestion: Reduce the duration of the non-compete clause to a more enforceable period (e.g., 1 year)."
            )

        if "indemnity" in clause.lower():
            suggestion += (
                " Suggestion: Clarify indemnity terms to ensure they are fair and limited to foreseeable damages."
            )

        # Append tailored suggestion
        suggestions.append(suggestion)

    # Default message if no manipulative clauses were detected
    if not suggestions:
        suggestions.append("No high-risk manipulative clauses were detected. The document appears well-written.")

    return suggestions


def local_gif_to_base64(path):
    with open(path, "rb") as gif_file:
        encoded_gif = base64.b64encode(gif_file.read()).decode("utf-8")
    return f"data:image/gif;base64,{encoded_gif}"




# Streamlit GUI Implementation with QA History
def app2():


    emoji_map = {
        "neutral": f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735470429700.gif')}' style='width:48px; height:48px;'>",
        "joy":f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735470670415.gif')}' style='width:48px; height:48px;'>",
        "sadness":f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735470963088.gif')}' style='width:48px; height:48px;'>",
        "anger":f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735471042020.gif')}' style='width:48px; height:48px;'>",
        "surprise": f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735471386722.gif')}' style='width:48px; height:48px;'>",
        "fear": f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735471457258.gif')}' style='width:48px; height:48px;'>",
        "disgust":f"<img src='{local_gif_to_base64('C:/Users/patta/Downloads/Animation - 1735470670415.gif')}' style='width:48px; height:48px;'>"
    }
    # Add background styling
    st.markdown(
        """
        <style>
        /* Set the background image with full clarity */
        .stApp {
            background-image: url("");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }

        /* Add transparency to the main content to make the background visible */
        .stApp > div:first-child > div {
            background: rgba(255, 255, 255, 0.8); /* Slightly transparent */
            border-radius: 10px;
            padding: 15px;
        }

        /* Customize font and text color */
        h1, h2, h3, h4, h5, h6 {
            color: #1e293b; /* Dark color for headings */
        }
        body, p {
            color: #334155; /* General text color */
        }

        /* Style buttons */
        .stButton button {
            background-color: #4CAF50; /* Green button color */
            color: white;
            border-radius: 5px;
            padding: 10px;
            border: none;
        }

        /* Style text area */
        .stTextArea textarea {
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }

        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Contract Analyzer")
    st.write("Upload a contract document and interact with it using advanced features.")

    # File upload
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        # Extract text
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.write("### Extracted Text")
        st.text_area("PDF Content", pdf_text, height=300)

        st.write("### Edit Extracted Text")
        edited_text = st.text_area("Edit PDF Content", pdf_text, height=300)

        if st.button("Save Edited Content"):
            try:
                # Save the edited content to a text file with UTF-8 encoding
                with open("edited_content.txt", "w", encoding="utf-8") as file:
                    file.write(edited_text)
                st.success("Edited content saved successfully!")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        # Summarization
        if st.button("Summarize Document"):
            summarized_text = summarize_text(pdf_text)
            st.write("### Summarized Text")
            st.text_area("Summary", summarized_text, height=200)

            # Add Download Button
            st.download_button(
                label="Download Summary",
                data=summarized_text,
                file_name="summary.txt",
                mime="text/plain"
            )

        # Behavioral Manipulation
        if st.button("Detect Behavioral Manipulation"):
            flagged_clauses = detect_behavioral_manipulation(pdf_text)
            if flagged_clauses:
                st.write("*Behavioral Manipulation Detection Report:*")
                for clause, issue in flagged_clauses.items():
                    st.write(f"*Sentence:* {clause}")
                    st.write(f"- {issue}")
            else:
                st.write("No high-risk manipulative language detected in the document.")

        # Sentiment and Emotion Analysis
        if st.button("Perform Sentiment and Emotion Analysis"):
            emotions = sentiment_emotion_analysis(pdf_text)
            st.write("### Top Emotions Detected")
            for emotion, score in emotions[:3]:
                emoji = emoji_map.get(emotion, "")
                st.markdown(
                    f"<div style='display: flex; align-items: center;'>"
                    f"<span style='margin-right: 10px;'>{emotion}: {score:.2f}</span>"
                    f"{emoji}"
                    f"</div>",
                    unsafe_allow_html=True
                )

        if st.button("Generate Suggestions"):

            flagged_clauses = detect_behavioral_manipulation(pdf_text)
            suggestions = generate_dynamic_suggestions(flagged_clauses, pdf_text)
            st.write("*Dynamic Suggestions for Manipulative Clauses:*")
            for suggestion in suggestions:
                st.write(suggestion)


        # QA Section with History
        st.write("## Question and Answer Section")
        if "qa_history" not in st.session_state:
            st.session_state.qa_history = []

        question = st.text_input("Ask a Question About the Document:")
        if question and st.button("Get Answer"):
            answer = advanced_question_answering(question, pdf_text)
            st.write("### Answer")
            st.write(answer)

            # Save to history
            st.session_state.qa_history.append({"question": question, "answer": answer})

        # Display QA History
        if st.session_state.qa_history:
            st.write("### Question and Answer History")
            for i, qa in enumerate(st.session_state.qa_history, 1):
                st.write(f"**Q{i}: {qa['question']}**")
                st.write(f"- **A{i}: {qa['answer']}**")

