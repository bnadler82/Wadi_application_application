import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Page Configuration
st.set_page_config(page_title="Lead Enrichment & Personalization Engine", page_icon="🎯", layout="wide")

st.title("🎯 AI Lead Enrichment & Personalization Engine")
st.caption("Automated company research, marketing bottleneck identification, and hyper-personalized outreach generation.")

# 1. Validate Streamlit Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🔑 Missing API Key! Please add `GEMINI_API_KEY` to your Streamlit Secrets.")
    st.stop()

# 2. Initialize Gemini Client
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

try:
    client = get_gemini_client()
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()

# 3. Sidebar Configuration
st.sidebar.header("Outreach Settings")
sender_name = st.sidebar.text_input("Your Name", value="Benjamin Nadler")
sender_role = st.sidebar.text_input("Your Role", value="Product Marketing Manager")
creativity = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)

# 4. Main App Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Target Prospect Info")
    company_name = st.text_input("Company Name", placeholder="e.g., Acme Corp")
    company_domain = st.text_input("Company Website (Optional)", placeholder="e.g., www.acme.com")
    prospect_name = st.text_input("Prospect Name", placeholder="e.g., Jane Doe")
    prospect_role = st.text_input("Prospect Role/Title", placeholder="e.g., Head of Growth")
    
    additional_context = st.text_area(
        "Extra Context / Observations", 
        placeholder="e.g., They recently launched a new SaaS platform, but their blog hasn't been updated in 6 months..."
    )
    
    submit_button = st.button("🚀 Analyze & Generate Outreach", use_container_width=True)

# 5. Pipeline Execution
if submit_button:
    if not company_name or not prospect_name:
        st.warning("⚠️ Please provide at least the Company Name and Prospect Name to start.")
    else:
        with col2:
            st.subheader("Analysis & Outreach Output")
            
            # Step 1: Deep Research & Bottleneck Analysis
            with st.spinner("🕵️‍♂️ Researching company and finding marketing gaps..."):
                research_prompt = f"""
                You are an expert growth marketer and product marketing manager. 
                Conduct an analysis on the company '{company_name}' ({company_domain if company_domain else 'No website provided'}).
                
                Additional notes provided: {additional_context if additional_context else 'None'}
                
                Provide a structured report covering:
                1. Main value proposition of the company.
                2. Potential marketing bottlenecks or growth gaps they face (e.g., gaps in content strategy, share of voice, performance marketing, conversion optimization).
                """
                
                try:
                    # Using Google Search Grounding to simulate live research if available, or deep reasoning via flash
                    research_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=research_prompt,
                        config=types.GenerateContentConfig(
                            temperature=creativity,
                            # Optional: adds live Google Search to ground the analysis if domain is real
                            tools=[{"google_search": {}}] if company_domain else None 
                        )
                    )
                    research_result = research_response.text
                    
                    with st.expander("📊 View Company Research & Bottlenecks", expanded=True):
                        st.markdown(research_result)
                        
                except APIError as e:
                    st.error(f"API Error during research: {e}")
                    st.stop()
            
            # Step 2: Personalized Outreach Generation
            with st.spinner("✍️ Crafting hyper-personalized email pipeline..."):
                email_prompt = f"""
                Based on the following research about {company_name}:
                ---
                {research_result}
                ---
                
                Write a high-converting, personalized cold outreach email to {prospect_name}, who is the {prospect_role}.
                The email must explicitly tie back to one of the identified marketing bottlenecks and offer a clear, low-friction value add.
                
                Sender Info:
                - Name: {sender_name}
                - Title: {sender_role}
                
                Guidelines:
                - Subject line must be punchy and highly relevant (no cheesy clickbait).
                - Keep the email body short, professional, and entirely focused on helping THEM scale or solve a technical efficiency gap.
                - Do not sound like a generic template.
                """
                
                try:
                    email_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=email_prompt,
                        config=types.GenerateContentConfig(temperature=creativity)
                    )
                    
                    st.success("✉️ Generated Outreach Email")
                    st.code(email_response.text, language="markdown")
                    
                except APIError as e:
                    st.error(f"API Error during email generation: {e}")
