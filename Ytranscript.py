from youtube_transcript_api import YouTubeTranscriptApi
import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ===== API Key Handling =====
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    api_key = st.text_input(
        "Enter your Google Generative AI API Key:", type="password")
    if not api_key:
        st.info("Please enter your API key to continue.", icon="🗝️")
        st.stop()
    else:
        st.success("API key received. Verifying...")

try:
    genai.configure(api_key=api_key)
    test_model = genai.GenerativeModel("gemini-1.5-flash-001")
    _ = test_model.generate_content("Hello!").text
except Exception as e:
    st.error("Invalid or unauthorized API key. Please double-check and try again.")
    st.stop()

# ✅ Define prompt for Gemini
prompt = [""" 
You are a YouTube transcript summarizer.

Your task is to summarize the transcript of a YouTube video and
provide it in clean, concise bullet points in less than 500 words.

At the end, show the total number of words in the original transcript.  
 """]

# ✅ Extract transcript from a YouTube URL


def extract_transcript_details(youtube_url):
    try:
        video_id = youtube_url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript])
        return transcript_text, video_id
    except Exception as e:
        st.error(f"❌ Error fetching transcript: {e}")
        return None, None

# ✅ Generate summary using Gemini


def generate_gemini_summary(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([prompt[0], transcript_text])
    return response.text if response and response.text else "No response generated."


# ✅ Streamlit UI
st.title("🎬 YouTube Transcript Summarizer")
st.write("Paste a YouTube URL below to fetch and summarize its transcript:")

youtube_link = st.text_input("🔗 YouTube Video URL")

if youtube_link:
    transcript_text, video_id = extract_transcript_details(youtube_link)

    if transcript_text:
        # st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        st.write("✅ Transcript fetched successfully.")

        if st.button("🧠 Generate Summary"):
            with st.spinner("Generating summary using Gemini..."):
                summary = generate_gemini_summary(transcript_text, prompt)
                st.markdown("### ✍️ Summary:")
                st.write(summary)
                st.markdown(
                    f"**Transcript length:** `{len(transcript_text.split())}` words")
    else:
        st.error("❌ No transcript available for this video.")
