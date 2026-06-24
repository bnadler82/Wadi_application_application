import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Page Configuration
st.set_page_config(page_title="LLM Optimization Auditor", page_icon="🔍", layout="wide")

st.title("🔍 LLM Optimization & Visibility Auditor")
st.caption("Evaluate how your website is parsed, understood, and cited by Large Language Models.")

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

# 3. Sidebar: Context & Alignment Parameters
st.sidebar.header("🎯 Strategic Context Alignment")
st.sidebar.info("Provide the baseline context so the LLM audits the domain accurately against your target market.")

industry = st.sidebar.text_input("Target Industry", placeholder="e.g., Cybersecurity SaaS, B2B MarTech")
strategic_angle = st.sidebar.text_area(
    "Strategic Angle / Differentiator", 
    placeholder="e.g., We focus heavily on data privacy compliance and technical automation for enterprise infrastructure."
)
target_demographic = st.sidebar.text_input("Target Demographic", placeholder="e.g., CISOs, Heads of Growth, IT Directors")

# 4. Main App Interface - Inputs
st.subheader("Company Website to Audit")
col1, col2 = st.columns([1, 1])

with col1:
    company_name = st.text_input("Company Name", placeholder="e.g., Acme Corp")
    company_url = st.text_input("Website URL", placeholder="e.g., https://www.acme.com")
    
    submit_button = st.button("🚀 Run LLM Visibility Audit", use_container_width=True)

# 5. Audit Execution Pipeline
if submit_button:
    if not company_name or not company_url:
        st.warning("⚠️ Please provide both the Company Name and Website URL to run the audit.")
    elif not industry or not target_demographic:
        st.warning("⚠️ Please fill out the Industry and Target Demographic in the sidebar to ensure proper context alignment.")
    else:
        with col2:
            st.subheader("LLM Audit Report")
            
            with st.spinner(f"🕵️‍♂️ Fetching and analyzing {company_name}'s digital footprint for LLM readiness..."):
                audit_prompt = f"""
                You are an expert AI Search Optimization (GEO) and technical marketing consultant. 
                Your task is to audit the company '{company_name}' ({company_url}) to determine how effectively it positions itself to be understood, categorized, and recommended by Large Language Models (LLMs) and AI Search Engines (like Perplexity, Gemini, and OpenAI Search).
                
                CRITICAL CONTEXT ALIGNMENT PARAMETERS:
                - Target Industry: {industry}
                - Strategic Angle/Value Proposition: {strategic_angle if strategic_angle else 'Not specified'}
                - Target Demographic/Decision Maker: {target_demographic}
                
                Please generate a structured, professional audit covering the following two core pillars:

                ### 1. TECHNICAL READINESS SIDE
                - **Indexability & Crawling:** Analyze potential risks with LLM user-agents (e.g., GPTBot, Google-Extended) and robots.txt posture.
                - **Structured Data & Schema:** Highlight how they should use Schema markup (e.g., Product, Organization, TechArticle) to reinforce entity data for LLM knowledge graphs.
                - **Entity Association:** Evaluate how clearly the site's metadata defines "who they are" and "what they do" within their target industry.

                ### 2. LANGUAGE & CONTENT STRATEGY SIDE
                - **Information Density:** Evaluate if the content directly answers core industry questions or if it relies too heavily on vague marketing fluff that confuses LLM embeddings.
                - **Clarity of Entity & Concept Associations:** How well does the content map to the specific strategic angle and target demographic mentioned above?
                - **Objectivity & Authority Tone:** LLMs favor objective, high-utility content for citations. Analyze the tone of the copy.

                ### 3. ACTIONABLE IMPROVEMENT SUGGESTIONS
                Provide a concrete, bulleted checklist of changes to make on the technical side and content side to improve LLM visibility and citation rates.
                """
                
                try:
                    # Utilizing Live Search grounding to evaluate the company's real-time footprint
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=audit_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.4, # Lower temperature for analytical rigor
                            tools=[{"google_search": {}}]
                        )
                    )
                    
                    st.success("✅ Audit Complete!")
                    st.markdown(response.text)
                    
                except APIError as e:
                    st.error(f"API Error during the audit pipeline: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
