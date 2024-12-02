import streamlit as st
import os
from dotenv import load_dotenv
from prfaq_generator import PRFAQGenerator
import tempfile
import wandb
import random

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Amazon-style PRFAQ Generator",
    page_icon="📄",
    layout="wide"
)

def main():
    st.title("Amazon-style PRFAQ Generator")
    st.markdown("""
    Generate comprehensive PRFAQ documents following Amazon's six-pager format.
    Enter your product description and requirements below.
    """)

    # Initialize session state
    if 'generated_doc' not in st.session_state:
        st.session_state.generated_doc = None

    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if not api_key:
            st.warning("Please enter your OpenAI API key to continue.")
            return

    # Text input for product description
    product_desc = st.text_area(
        "Product Description and Requirements",
        height=200,
        placeholder="Enter your product description and requirements here..."
    )

    # Generate button
    if st.button("Generate PRFAQ"):
        if not product_desc:
            st.error("Please enter a product description.")
            return

        with st.spinner("Generating PRFAQ document... This may take a few minutes."):
            try:
                generator = PRFAQGenerator(api_key)
                doc = generator.create_document(product_desc)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    doc.save(tmp_file.name)
                    st.session_state.generated_doc = tmp_file.name
                
                st.success("PRFAQ document generated successfully!")
                
                # Download button
                with open(st.session_state.generated_doc, 'rb') as file:
                    st.download_button(
                        label="Download PRFAQ Document",
                        data=file,
                        file_name="PRFAQ_Document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Cleanup temporary file
    if st.session_state.generated_doc and os.path.exists(st.session_state.generated_doc):
        try:
            os.unlink(st.session_state.generated_doc)
        except:
            pass

    # start a new wandb run to track this script
    wandb.init(
        # set the wandb project where this run will be logged
        project="wandbtest",           

        # track hyperparameters and run metadata
        config={
        "learning_rate": 0.02,
        "architecture": "CNN",
        "dataset": "CIFAR-100",
        "epochs": 10,
        }
    )

    # simulate training
    epochs = 10
    offset = random.random() / 5
    for epoch in range(2, epochs):
        acc = 1 - 2 ** -epoch - random.random() / epoch - offset
        loss = 2 ** -epoch + random.random() / epoch + offset

        # log metrics to wandb
        wandb.log({"acc": acc, "loss": loss})

    # [optional] finish the wandb run, necessary in notebooks
    wandb.finish()

if __name__ == "__main__":
    main()
