import streamlit as st
from utils.pdf_reader import extract_pdf_text
from utils.text import top_keywords, summarize_text
from services import rag
from services import llm

st.set_page_config(page_title="AI Podcast Assistant", layout="wide")
st.title("AI Podcast Assistant")
st.caption("Upload any PDF and get an LLM summary with trusted context (Wikipedia, Semantic Scholar, OpenAlex).")

with st.sidebar:
    mode = st.radio("Summarization mode", ["LLM (Hugging Face)", "Local (no key)"], index=0)
    top_wiki = st.slider("Wikipedia articles", 0, 5, 3)
    top_s2   = st.slider("Semantic Scholar papers", 0, 10, 4)
    top_oa   = st.slider("OpenAlex works", 0, 10, 3)
    st.caption("Keys live in environment vars only. No secrets in app.py.")

uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
manual_query = st.text_input("Optional: override query keywords (e.g., 'LLMs for marketing analytics')")

if uploaded:
    with st.spinner("Extracting text..."):
        text = extract_pdf_text(uploaded)
    if not text:
        st.error("Could not read PDF."); st.stop()

    st.success(f"Loaded **{uploaded.name}** ({len(text):,} chars).")
    kw = top_keywords(text, k=8)
    query = manual_query.strip() or " ".join(kw[:6])

    st.markdown("#### Auto keywords")
    st.write(", ".join(kw) if kw else "—")
    st.markdown("#### Query")
    st.write(query or "—")

    # Adjust rag gather sizes
    rag.gather_context.__defaults__ = (top_wiki, top_s2, top_oa)

    if mode.startswith("LLM"):
        if not llm.available():
            st.warning("LLM not configured; falling back to local summary.")
            st.write(summarize_text(text, max_sentences=8))
        else:
            with st.spinner("Summarizing with LLM + external context..."):
                out = rag.summarize_with_context(text, query)
            st.markdown("### Summary (LLM)")
            st.write(out)
    else:
        with st.spinner("Creating local summary..."):
            out = summarize_text(text, max_sentences=8)
        st.markdown("### Summary (Local)")
        st.write(out)
else:
    st.info("Upload a PDF to begin.")
