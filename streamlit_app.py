import streamlit as st
from google import genai
from google.genai.errors import APIError

# Set up the page title and icon
st.set_page_config(page_title="Gemini Chat Assistant", page_icon="🤖")
st.title("🤖 Gemini AI Assistant")

# 1. Check for the API key in Streamlit Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add `GEMINI_API_KEY` to your Streamlit Secrets.")
    st.stop()

# 2. Initialize the Gemini client
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

try:
    client = get_gemini_client()
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()

# 3. Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display past chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle new user input
if user_input := st.chat_input("Ask me anything..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Add user message to session history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response from Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*Thinking...*")
        
        try:
            # Using gemini-2.5-flash for fast, efficient text generation
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_input,
            )
            
            output_text = response.text
            message_placeholder.markdown(output_text)
            
            # Add assistant response to session history
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except APIError as e:
            message_placeholder.markdown("❌ **API Error:** Please check your API key or network connection.")
            st.sidebar.error(f"Detailed Error: {e}")
        except Exception as e:
            message_placeholder.markdown("❌ An unexpected error occurred.")
            st.sidebar.error(f"Detailed Error: {e}")
