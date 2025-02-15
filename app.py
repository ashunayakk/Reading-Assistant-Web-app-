import streamlit as st
import pdfplumber
from gtts import gTTS
import concurrent.futures
import cv2
import easyocr
import os

# Title and Description
st.title("📚 Enhanced Reading Assistance App")
st.write("Upload a PDF or image file, and the app will extract the text and read it aloud!")

# Session state for control
if "stop" not in st.session_state:
    st.session_state.stop = False
if "reading" not in st.session_state:
    st.session_state.reading = False

# File Upload
uploaded_file = st.file_uploader("Upload a PDF or image file", type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF files."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text.strip()

def extract_text_from_image(image_file):
    """Extract text from images using OCR."""
    try:
        image = cv2.imread(image_file)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(['en'])  # You can add more languages here
        result = reader.readtext(gray_image, detail=0)
        extracted_text = " ".join(result)
        return extracted_text.strip()
    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
        return ""

def generate_audio(text):
    """Generate audio from text with error handling."""
    try:
        tts = gTTS(text=text.strip(), lang='en')  # You can add language selection here
        tts.save("output.mp3")
        return "output.mp3"
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

# Main Processing
if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_extension in ["png", "jpg", "jpeg"]:
        # Save the uploaded image temporarily
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_file.read())
        extracted_text = extract_text_from_image("temp_image.jpg")
        # Remove temporary image file (optional)
        os.remove("temp_image.jpg")
    else:
        st.error("Unsupported file type. Please upload a PDF or image file.")
        extracted_text = ""

    if extracted_text.strip():
        st.subheader("🖍 Extracted Text:")
        st.text_area("Extracted Text:", value=extracted_text, height=300)

        # Read Aloud Button
        if st.button("🔊 Read Aloud"):
            if not st.session_state.reading:
                st.session_state.stop = False
                st.session_state.reading = True
                with st.spinner("Generating audio..."):
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        audio_file = executor.submit(generate_audio, extracted_text).result()
                    if audio_file:
                        st.audio(audio_file, format="audio/mp3")
                        st.session_state.reading = False
            else:
                st.warning("Reading is already in progress. Please wait or click 'Stop'.")

        # Stop Button (Not very effective with asynchronous processing)
        if st.button("⏹ Stop Reading"):
            st.session_state.stop = True  # This might not stop the audio immediately
    else:
        st.error("No readable text found in the uploaded file. Please try another file.")
else:
    st.info("Please upload a PDF or image file to begin.")