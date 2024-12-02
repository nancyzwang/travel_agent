import streamlit as st
import os
from linkedin_paper_assistant import LinkedInPaperAssistant
import time

# Set page config
st.set_page_config(
    page_title="Research Paper to LinkedIn Post",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        width: 100%;
    }
    .output-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d1f2eb;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #fadbd8;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_assistant():
    if 'assistant' not in st.session_state:
        st.session_state.assistant = LinkedInPaperAssistant()

def main():
    st.title("📚 Research Paper to LinkedIn Post Converter")
    st.markdown("""
    Transform academic papers into engaging LinkedIn posts! 
    Just paste the arXiv URL of the paper you want to share.
    """)

    initialize_assistant()

    # Input section
    st.header("📄 Paper Input")
    paper_url = st.text_input(
        "Enter arXiv paper URL (e.g., https://arxiv.org/abs/2405.18749)",
        placeholder="https://arxiv.org/abs/XXXX.XXXXX"
    )

    # Process button
    if st.button("🔄 Process Paper", type="primary"):
        if not paper_url:
            st.error("Please enter a paper URL")
            return

        try:
            with st.spinner("🔍 Downloading and processing paper..."):
                # Extract text from PDF
                paper_text = st.session_state.assistant.extract_text_from_pdf_url(paper_url)
                st.session_state.paper_text = paper_text

            with st.spinner("📊 Analyzing paper..."):
                # Analyze paper
                analysis = st.session_state.assistant.analyze_paper(paper_text)
                st.session_state.analysis = analysis

            with st.spinner("✍️ Creating LinkedIn post..."):
                # Generate LinkedIn post
                linkedin_post = st.session_state.assistant.create_linkedin_post(analysis)
                st.session_state.linkedin_post = linkedin_post

            # Display results
            st.success("Processing complete! 🎉")
            
            # Results section
            st.header("📊 Analysis Results")
            with st.expander("View Paper Analysis", expanded=True):
                st.markdown(f'''
                <div class="output-box">
                {analysis}
                </div>
                ''', unsafe_allow_html=True)

            st.header("📱 LinkedIn Post")
            with st.expander("View LinkedIn Post", expanded=True):
                st.markdown(f'''
                <div class="success-box">
                {linkedin_post}
                </div>
                ''', unsafe_allow_html=True)

                # Copy button
                if st.button("📋 Copy Post to Clipboard"):
                    try:
                        st.write("Post copied to clipboard! 📋")
                        st.session_state.clipboard = linkedin_post
                    except Exception as e:
                        st.error(f"Error copying to clipboard: {str(e)}")

        except Exception as e:
            st.error(f"Error processing paper: {str(e)}")
            st.markdown(f'''
            <div class="error-box">
            Please make sure:
            - The URL is a valid arXiv paper URL
            - The paper is publicly accessible
            - You have a stable internet connection
            </div>
            ''', unsafe_allow_html=True)

    # Help section
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. **Find a Paper**: Go to arXiv and find a paper you want to share
        2. **Copy URL**: Copy the paper's URL (e.g., https://arxiv.org/abs/2405.18749)
        3. **Paste & Process**: Paste the URL above and click "Process Paper"
        4. **Review & Share**: Copy the generated LinkedIn post and share it!
        
        **Tips**:
        - The analysis provides a detailed breakdown of the paper
        - The LinkedIn post is optimized for engagement
        - You can copy the post directly to your clipboard
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ using Together AI | "
        "Share your research insights professionally!"
    )

if __name__ == "__main__":
    main()
