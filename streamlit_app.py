import streamlit as st
import openai
import json

# App Layout Configuration
st.set_page_config(page_title="WadiDigital Lead Gen Engine", page_icon="🎯", layout="wide")

st.title("🎯 AI Lead Enrichment & Personalization Engine")
st.subheader("Turn a simple company name into a deeply researched, hyper-targeted outreach campaign.")

# Sidebar Configuration
st.sidebar.header("🔑 Authentication")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

st.markdown("---")

# User Inputs
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏢 Prospect Information")
    company_name = st.text_input("Target Company Name", placeholder="e.g., CyberShield")
    company_domain = st.text_input("Company Website/Domain (Optional)", placeholder="e.g., cybershield.io")
    
with col2:
    st.markdown("### 👥 Strategy Settings")
    target_persona = st.text_input("Decision Maker Title", value="VP of Marketing")
    value_proposition = st.text_area(
        "What are we selling them? (Wadi's Value Prop)", 
        value="We help high-growth tech companies capture market share in AI search engines (ChatGPT, Perplexity) using advanced GEO strategies."
    )

# Execution Engine
if st.button("🚀 Enrich Lead & Generate Campaign"):
    if not api_key:
        st.error("Please provide an OpenAI API Key in the sidebar to run the automation pipeline.")
    elif not company_name:
        st.warning("Please enter a target company name.")
    else:
        with st.spinner(f"Analyzing {company_name}'s market footprint and drafting copy..."):
            try:
                client = openai.OpenAI(api_key=api_key)
                
                # STEP 1: Enrichment Prompt (Simulating deep research)
                enrichment_system = (
                    "You are an elite B2B growth marketer and corporate researcher. "
                    "Analyze the given company name and domain. Deduce their likely industry, "
                    "their business model (B2B/B2C), three major marketing bottlenecks they are facing, "
                    "and how they are likely losing ground to competitors in AI search results. "
                    "Return your analysis strictly as a JSON object with the keys: "
                    "'industry', 'business_model', 'pain_points' (list of 3 points), and 'ai_search_vulnerability'."
                )
                
                enrich_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={ "type": "json_object" },
                    messages=[
                        {"role": "system", "content": enrichment_system},
                        {"role": "user", "content": f"Company: {company_name}, Domain: {company_domain}"}
                    ],
                    temperature=0.4
                )
                
                lead_data = json.loads(enrich_response.choices[0].message.content)
                
                # Display Enriched Data Profile
                st.success("🎉 Lead Enrichment Complete!")
                
                st.markdown("## 📊 Enriched Prospect Profile")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.metric("Inferred Industry", lead_data.get("industry", "Unknown"))
                    st.write("**Identified Marketing Bottlenecks:**")
                    for point in lead_data.get("pain_points", []):
                        st.write(f"• {point}")
                with p_col2:
                    st.metric("Business Model", lead_data.get("business_model", "Unknown"))
                    st.warning(f"**AI Search Weakness:** {lead_data.get('ai_search_vulnerability')}")
                
                st.markdown("---")
                
                # STEP 2: Personalized Copy Generation (Prompt Chaining)
                st.markdown("## ✉️ Tailored Outreach Copy")
                
                copy_system = (
                    "You are a master of contextual, non-spammy B2B copywriting. "
                    "Write a highly engaging, short cold email to the decision maker. "
                    "Use the prospect's profile data to weave in specific context naturally. "
                    "Do not use generic fluff. Hook them based on their specific AI search vulnerabilities. "
                    "Format the response into clear sections: 'Subject Line', 'Email Body'."
                )
                
                user_context = f"""
                Prospect: {company_name} ({target_persona})
                Prospect Data: {json.dumps(lead_data)}
                Our Offer: {value_proposition}
                """
                
                copy_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "copy_system": copy_system},
                        {"role": "user", "content": user_context}
                    ],
                    temperature=0.7
                )
                
                outreach_text = copy_response.choices[0].message.content
                st.text_area("Generated High-Conversion Email", value=outreach_text, height=350)
                
            except Exception as e:
                st.error(f"Pipeline error: {str(e)}")
