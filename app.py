"""
Multi-Agent Research Assistant — Streamlit Web Application
A sleek, professional single-page dashboard demonstrating coordinated LLM agents
for autonomous web research, grounded synthesis, and fact-checking.
"""

import json
import os
import time
from datetime import datetime

# Load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st


def get_groq_api_key() -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    return key


from agents.coordinator import Coordinator, DEFAULT_MODEL



# ==============================================================================
# Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Multi-Agent Research Assistant — Built by Mohamed Islam."
    },
)

# ==============================================================================
# Custom CSS Styling (Executive Dark Minimalist & Glassmorphism Theme)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Completely hide sidebar and Streamlit default header controls */
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stHeaderActionElements"],
    [data-testid="stToolbar"],
    button[kind="header"] {
        display: none !important;
    }

    /* Modern Dark Theme Background */
    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.07) 0%, transparent 45%),
                    radial-gradient(circle at 90% 90%, rgba(56, 189, 248, 0.07) 0%, transparent 45%),
                    #090d16;
        color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1140px;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Fixed / Auto-Expanding Textarea (No manual drag resize handle) */
    [data-testid="stTextArea"] textarea,
    textarea {
        resize: none !important;
        field-sizing: content !important;
        min-height: 100px !important;
        max-height: 380px !important;
        border-radius: 12px !important;
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #f8fafc !important;
        overflow-y: auto !important;
        line-height: 1.5 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    [data-testid="stTextArea"] textarea:focus,
    textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    }


    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.8rem 1rem;
        margin-bottom: 1.5rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 14px;
        border-radius: 100px;
        margin-bottom: 1.1rem;
    }

    .hero-heading {
        font-size: 2.85rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
        line-height: 1.15;
    }

    .hero-subheading {
        color: #94a3b8;
        font-size: 1.1rem;
        max-width: 780px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Agent Stepper Cards */
    .agent-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.15rem 1.1rem;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
    }

    .agent-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.35);
    }

    .agent-pill {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #818cf8;
        background: rgba(99, 102, 241, 0.1);
        padding: 2px 7px;
        border-radius: 5px;
        margin-bottom: 0.45rem;
    }

    .agent-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }

    .agent-desc {
        color: #94a3b8;
        font-size: 0.82rem;
        line-height: 1.45;
        margin-bottom: 0;
    }

    /* Metrics Row */
    .metric-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        text-align: center;
    }

    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #38bdf8;
    }

    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 2px;
    }

    /* Source Cards Grid */
    .source-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.85rem;
        transition: all 0.2s ease;
    }

    .source-card:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(56, 189, 248, 0.35);
    }

    .source-id {
        display: inline-block;
        background: #6366f1;
        color: #ffffff;
        font-size: 0.7rem;
        font-weight: 700;
        border-radius: 4px;
        padding: 2px 7px;
        margin-right: 6px;
    }

    .source-title-link {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f5f9;
        text-decoration: none;
    }

    .source-title-link:hover {
        color: #38bdf8;
        text-decoration: underline;
    }

    .source-snippet {
        color: #94a3b8;
        font-size: 0.84rem;
        margin-top: 0.45rem;
        line-height: 1.45;
    }

    .source-query {
        color: #64748b;
        font-size: 0.74rem;
        margin-top: 0.35rem;
        font-style: italic;
    }

    /* Primary & Download Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.02em;
        padding: 0.65rem 1.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border: none;
        color: #ffffff;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        box-shadow: 0 8px 20px -4px rgba(99, 102, 241, 0.5);
    }

    .stDownloadButton > button {
        border-radius: 12px;
        font-weight: 600;
        background: #1e293b;
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.12);
        width: 100%;
    }

    .stDownloadButton > button:hover {
        background: #334155;
        border-color: #6366f1;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# Hero Section
# ==============================================================================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-badge">⚡ Autonomous Agentic Intelligence</div>
        <div class="hero-heading">Multi-Agent Research Assistant</div>
        <div class="hero-subheading">
            Decomposes complex research questions, harvests real-time web knowledge across parallel sub-queries,
            synthesizes inline-cited answers, and validates factual grounding before delivery.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4-Stage Architecture Stepper Cards
stepper_cols = st.columns(4)
with stepper_cols[0]:
    st.markdown(
        """
        <div class="agent-card">
            <span class="agent-pill">Stage 1</span>
            <div class="agent-title">🎯 Coordinator</div>
            <p class="agent-desc">Deconstructs topic, orchestrates pipeline state, and formats final dossier.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with stepper_cols[1]:
    st.markdown(
        """
        <div class="agent-card">
            <span class="agent-pill">Stage 2</span>
            <div class="agent-title">🔍 Search Agent</div>
            <p class="agent-desc">Plans targeted sub-queries and harvests real-time web intelligence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with stepper_cols[2]:
    st.markdown(
        """
        <div class="agent-card">
            <span class="agent-pill">Stage 3</span>
            <div class="agent-title">📝 Summarizer</div>
            <p class="agent-desc">Synthesizes extracted findings into a cohesive, inline-cited draft [1].</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with stepper_cols[3]:
    st.markdown(
        """
        <div class="agent-card">
            <span class="agent-pill">Stage 4</span>
            <div class="agent-title">🛡️ Fact-Checker</div>
            <p class="agent-desc">Cross-references claims against source snippets, flagging unbacked facts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)


# ==============================================================================
# Research Query & Launch Section
# ==============================================================================
sample_queries = [
    "What are the main approaches to reducing hallucination in large language models?",
    "How do Graph RAG architectures compare to standard vector similarity RAG?",
    "What are the key trade-offs between LLM fine-tuning and retrieval-augmented generation?",
    "What are the latest paradigms and benchmarks for autonomous AI coding agents?",
]

selected_sample = st.selectbox("💡 Quick-fill sample research topic:", ["Custom Query..."] + sample_queries)
default_text = "" if selected_sample == "Custom Query..." else selected_sample

with st.form("live_research_form", clear_on_submit=False):
    question_input = st.text_area(
        "Research Question or Complex Topic",
        value=default_text,
        placeholder="e.g. What are the key architectural patterns for autonomous AI agents in 2026?",
        height=100,
    )
    submit_live = st.form_submit_button("⚡ Run Multi-Agent Research Pipeline", type="primary", use_container_width=True)

# Client-side auto-expansion listener
st.markdown(
    """
    <script>
    function setupAutoExpand() {
        const textareas = window.parent.document.querySelectorAll('textarea');
        textareas.forEach(ta => {
            ta.style.resize = 'none';
            function adjust() {
                ta.style.height = 'auto';
                ta.style.height = Math.min(Math.max(ta.scrollHeight, 100), 380) + 'px';
            }
            ta.removeEventListener('input', adjust);
            ta.addEventListener('input', adjust);
            adjust();
        });
    }
    setTimeout(setupAutoExpand, 300);
    setTimeout(setupAutoExpand, 1000);
    </script>
    """,
    unsafe_allow_html=True,
)


if submit_live:
    if not question_input.strip():
        st.warning("Please enter a research question.")
    else:
        # Real-time execution visualizer
        progress_container = st.container()
        with progress_container:
            st.markdown("#### 🔄 Agent Pipeline Execution Trace")
            status_box = st.status("Initializing Multi-Agent Coordinator...", expanded=True)

            def on_step_callback(agent, action, data):
                if agent == "SearchAgent" and action == "planning":
                    status_box.write("🎯 **Search Agent**: Formulating search strategy and generating sub-queries...")
                elif agent == "SearchAgent" and action == "query_complete":
                    status_box.write(f"🔍 **Search Agent**: Queried `{data.get('query')}` — Found {data.get('results_count')} results")
                elif agent == "SearchAgent" and action == "complete":
                    status_box.write(f"✅ **Search Agent**: Gathered {data.get('findings_count')} total grounded sources.")
                elif agent == "SummarizerAgent" and action == "synthesizing":
                    status_box.write("📝 **Summarizer Agent**: Synthesizing inline-cited draft answer...")
                elif agent == "SummarizerAgent" and action == "complete":
                    status_box.write("✅ **Summarizer Agent**: Draft synthesis complete.")
                elif agent == "FactCheckerAgent" and action == "verifying":
                    status_box.write("🛡️ **Fact-Checker Agent**: Cross-referencing draft claims with cited evidence...")
                elif agent == "FactCheckerAgent" and action == "complete":
                    status_box.write("✅ **Fact-Checker Agent**: Verification audit finished.")
                elif agent == "Coordinator" and action == "complete":
                    status_box.write(f"🏁 **Coordinator**: Executive report assembled in {data.get('elapsed_seconds')}s.")

            try:
                active_key = get_groq_api_key()
                coordinator = Coordinator(api_key=active_key)
                result_data = coordinator.run(

                    question=question_input.strip(),
                    num_queries=3,
                    max_results_per_query=4,
                    on_step=on_step_callback,
                    return_details=True,
                )
                status_box.update(label="✅ Research Pipeline Completed Successfully!", state="complete", expanded=False)
                st.session_state.current_data = result_data
                st.success("Executive Dossier generated and ready for review.")
            except Exception as exc:
                status_box.update(label="❌ Pipeline Execution Failed", state="error")
                st.error(f"Error during research workflow: {exc}")


# ==============================================================================
# Research Dossier Dashboard (Tabs, Metrics, Evidence, Exports)
# ==============================================================================
if "current_data" in st.session_state and st.session_state.current_data:
    data = st.session_state.current_data
    
    st.markdown("---")
    st.markdown(f"## 📑 Research Dossier: {data.get('question')}")

    flags_raw = str(data.get("flags", "")).strip()
    is_clean = not flags_raw or "no issues found" in flags_raw.lower() or "no issues" in flags_raw.lower() or "verified" in flags_raw.lower() or len(flags_raw) < 5
    status_text = "100% Grounded" if is_clean else "Audit Flags"
    status_color = "#10b981" if is_clean else "#f59e0b"

    # Metrics Summary Row
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{data.get('elapsed_seconds', 'N/A')}s</div>
                <div class="metric-label">⚡ Execution Time</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        sources_count = len(data.get('sources', []))
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{sources_count}</div>
                <div class="metric-label">📚 Cited Sources</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        subq_count = len(data.get('subqueries', []))
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{subq_count}</div>
                <div class="metric-label">🔍 Sub-Queries</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value" style="color: {status_color};">{'✅' if is_clean else '⚠️'} {status_text}</div>
                <div class="metric-label">🛡️ Fact Audit</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Tabs for Dossier Views
    tab_report, tab_trace, tab_sources, tab_export = st.tabs([
        "📄 Executive Dossier",
        "🔍 Agent Trace & Sub-Queries",
        "📚 Grounded Evidence Grid",
        "💾 Export & Raw Data",
    ])

    # Tab 1: Executive Dossier
    with tab_report:
        st.markdown("### 📋 Synthesized Findings")
        st.markdown(data.get("draft", ""))
        
        st.markdown("---")
        st.markdown("### 🛡️ Fact-Checker Audit")
        if is_clean:
            display_msg = flags_raw if flags_raw and len(flags_raw) > 5 else "All claims in the executive report are verified and grounded in the cited source material."
            st.success(f"**Verification Audit Passed:** {display_msg}")
        else:
            st.warning(f"**Verification Audit Notes:**\n\n{flags_raw}")


    # Tab 2: Agent Trace
    with tab_trace:
        st.markdown("### 🧠 Multi-Agent Execution Strategy")
        
        st.markdown("#### 1. Search Agent Decomposition")
        st.markdown("The Coordinator instructed the Search Agent to decompose the primary topic into targeted web search angles:")
        for idx, sq in enumerate(data.get("subqueries", []), 1):
            st.markdown(f"**Query {idx}:** `{sq}`")

        st.markdown("---")
        st.markdown("#### 2. Pipeline Metadata")
        st.json({
            "model_engine": data.get("model", DEFAULT_MODEL),
            "generated_at": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "total_findings_retrieved": len(data.get("findings", [])),
            "total_cited_sources": len(data.get("sources", [])),
        })

    # Tab 3: Sources Grid
    with tab_sources:
        st.markdown("### 🌐 Grounded Citations & Evidence")
        sources = data.get("sources", [])
        if sources:
            for s in sources:
                url = s.get("url", "#")
                domain = url.split("/")[2] if "//" in url else "web"
                st.markdown(
                    f"""
                    <div class="source-card">
                        <div>
                            <span class="source-id">[{s.get('id')}]</span>
                            <a href="{url}" target="_blank" class="source-title-link">{s.get('title', 'Untitled')}</a>
                            <span style="color: #64748b; font-size: 0.75rem; margin-left: 8px;">({domain})</span>
                        </div>
                        <div class="source-snippet">{s.get('snippet', 'No snippet available.')}</div>
                        {f"<div class='source-query'>Sub-query: {s.get('query')}</div>" if s.get('query') else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No external source metadata available.")

    # Tab 4: Export & Raw Data
    with tab_export:
        st.markdown("### 💾 Export Research Dossier")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.download_button(
                label="📥 Download Markdown Dossier (.md)",
                data=data.get("report", ""),
                file_name=f"research_dossier_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col_exp2:
            json_export = json.dumps(data, indent=2)
            st.download_button(
                label="📥 Download Structured JSON Data (.json)",
                data=json_export,
                file_name=f"research_data_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("#### Raw Report Markdown Preview")
        st.code(data.get("report", ""), language="markdown")

# Clean Minimalist Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1.25rem 0;">
        ⚡ <b>Multi-Agent Autonomous Research Assistant</b> · Developed by <a href="https://github.com/Mohamedislam42" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 600;">Mohamed Islam</a> · Powered by Groq LPU & LangChain
    </div>
    """,
    unsafe_allow_html=True,
)
