import streamlit as st
import sys
import os
import re
import time
from io import StringIO

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deep Research RAG Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Tokens ── */
  :root {
    --bg:        #0D0F14;
    --surface:   #141820;
    --surface2:  #1C2230;
    --border:    #252D3D;
    --accent:    #4F8EF7;
    --accent2:   #7B5EA7;
    --success:   #34C98A;
    --warn:      #F5A623;
    --text:      #E8ECF4;
    --muted:     #6B7A99;
    --radius:    12px;
  }

  /* ── Global ── */
  html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  }
  [data-testid="stHeader"] { background: transparent; }

  /* ── Hero ── */
  .hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    background: linear-gradient(160deg, #141820 0%, #0D1525 100%);
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
  }
  .hero-badge {
    display: inline-block;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 999px;
    padding: .25rem .85rem;
    margin-bottom: 1.1rem;
  }
  .hero h1 {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    letter-spacing: -.03em;
    background: linear-gradient(135deg, var(--accent) 0%, #A78BFA 60%, var(--success) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 .6rem;
  }
  .hero p {
    color: var(--muted);
    font-size: 1.05rem;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
  }

  /* ── Input card ── */
  .input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem 2rem;
    margin-bottom: 2rem;
  }

  /* ── Streamlit input override ── */
  [data-testid="stTextInput"] input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: .65rem 1rem !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,.18) !important;
  }

  /* ── Button ── */
  [data-testid="stButton"] button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: .95rem !important;
    padding: .6rem 2rem !important;
    transition: opacity .2s, transform .15s;
  }
  [data-testid="stButton"] button:hover {
    opacity: .88 !important;
    transform: translateY(-1px);
  }

  /* ── Pipeline steps ── */
  .step-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: .55rem;
  }
  .step-dot {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: .75rem; font-weight: 700; flex-shrink: 0;
  }
  .dot-wait   { background: var(--surface2); color: var(--muted); border: 1px solid var(--border); }
  .dot-active { background: var(--accent);   color: #fff; box-shadow: 0 0 10px rgba(79,142,247,.5); }
  .dot-done   { background: var(--success);  color: #fff; }
  .step-label { font-size: .9rem; }
  .step-label.muted { color: var(--muted); }
  .step-label.active { color: var(--text); font-weight: 600; }
  .step-label.done   { color: var(--success); }

  /* ── Result panels ── */
  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
  }
  .panel-header {
    display: flex; align-items: center; gap: .6rem;
    font-size: .78rem; font-weight: 700;
    letter-spacing: .1em; text-transform: uppercase;
    color: var(--muted); margin-bottom: .9rem;
  }
  .panel-header .dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
  .panel-content {
    color: var(--text);
    font-size: .93rem;
    line-height: 1.75;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .panel-content.report {
    font-size: .97rem;
  }

  /* ── Source chips ── */
  .source-chip {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: .25rem .8rem;
    margin: .2rem .3rem .2rem 0;
    font-size: .78rem;
    color: var(--muted);
  }
  .source-chip b { color: var(--accent); }

  /* ── Metric row ── */
  .metric-row {
    display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;
  }
  .metric-card {
    flex: 1; min-width: 140px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    text-align: center;
  }
  .metric-val  { font-size: 1.5rem; font-weight: 800; color: var(--accent); }
  .metric-lbl  { font-size: .78rem; color: var(--muted); margin-top: .15rem; }

  /* ── Divider ── */
  hr.fancy {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.8rem 0;
  }

  /* ── Scrollable result box ── */
  .scroll-box {
    max-height: 340px;
    overflow-y: auto;
    border-radius: 8px;
    background: var(--surface2);
    padding: 1rem 1.1rem;
  }
  .scroll-box::-webkit-scrollbar { width: 6px; }
  .scroll-box::-webkit-scrollbar-track { background: transparent; }
  .scroll-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

  /* hide streamlit default chrome */
  #MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
  [data-testid="stDecoration"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">Multi-Agent · RAG</div>
  <h1>Deep Research RAG Agent</h1>
  <p>Enter any topic and watch it search the web, scrape top sources, index them into a
  vector store, retrieve the most relevant chunks, then write and critique a grounded,
  cited report — end to end.</p>
</div>
""", unsafe_allow_html=True)


# ── Pipeline step renderer ─────────────────────────────────────────────────────
STEPS = [
    ("🔍", "Search Agent",   "Discovering recent, reliable sources"),
    ("🕸️", "Scraper",        "Fetching full text from top URLs"),
    ("📚", "Vector Index",   "Chunking & embedding into a vector store"),
    ("🎯", "Retriever",      "Retrieving the most relevant chunks for the topic"),
    ("✍️", "Writer Chain",   "Drafting the grounded, cited report"),
    ("🧐", "Critic Chain",   "Reviewing & scoring the report"),
]

STEP_RE = re.compile(r'Step (\d+)')


def render_steps(active: int):
    html = ""
    for i, (icon, name, desc) in enumerate(STEPS):
        if i < active:
            dot_cls, lbl_cls, label = "dot-done", "done", f"✓ {name}"
        elif i == active:
            dot_cls, lbl_cls, label = "dot-active", "active", f"{icon} {name} — {desc}…"
        else:
            dot_cls, lbl_cls, label = "dot-wait", "muted", f"{icon} {name}"
        html += f"""
        <div class="step-row">
          <div class="step-dot {dot_cls}">{i+1}</div>
          <span class="step-label {lbl_cls}">{label}</span>
        </div>"""
    return html


# ── Input area ─────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1], gap="medium")
    with col1:
        topic = st.text_input(
            "Research topic",
            placeholder="e.g.  Quantum computing breakthroughs in 2025",
            label_visibility="collapsed",
        )
    with col2:
        run = st.button("Run Research", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Main logic ─────────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Please enter a research topic before running.")
        st.stop()

    # ── Layout: steps left | results right ──────────────────────────────────
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown("#### Pipeline status")
        steps_placeholder = st.empty()
        steps_placeholder.markdown(render_steps(0), unsafe_allow_html=True)

    with right:
        result_placeholder = st.empty()

    # ── Import pipeline (deferred so Streamlit boots fast) ──────────────────
    try:
        from pipeline import run_research_pipeline
    except ImportError as e:
        st.error(f"Could not import pipeline.py: {e}\n\nMake sure this app.py lives in the same folder as pipeline.py.")
        st.stop()

    # ── We monkey-patch print to capture step progress ──────────────────────
    # The pipeline prints step banners ("Step N - ...") — we intercept them to update the UI.
    captured_steps = {"current": 0}
    original_print = print

    def ui_print(*args, **kwargs):
        text = " ".join(str(a) for a in args)
        match = STEP_RE.search(text)
        if match:
            captured_steps["current"] = int(match.group(1)) - 1
        steps_placeholder.markdown(
            render_steps(captured_steps["current"]),
            unsafe_allow_html=True,
        )
        original_print(*args, **kwargs)   # still log to terminal

    import builtins
    builtins.print = ui_print

    state = {}
    error = None
    start_ts = time.time()

    try:
        state = run_research_pipeline(topic.strip())
    except Exception as exc:
        error = exc
    finally:
        builtins.print = original_print   # always restore

    elapsed = time.time() - start_ts

    # ── Final step display ───────────────────────────────────────────────────
    if error:
        steps_placeholder.markdown(render_steps(captured_steps["current"]), unsafe_allow_html=True)
        with right:
            st.error(f"Pipeline error: {error}")
        st.stop()

    # All done
    steps_placeholder.markdown("""
    <div style="margin-top:.5rem">
      <div class="step-row"><div class="step-dot dot-done">✓</div>
        <span class="step-label done" style="font-weight:700">All steps complete</span></div>
    </div>""" + render_steps(99), unsafe_allow_html=True)

    # ── Metrics ─────────────────────────────────────────────────────────────
    with right:
        report_words = len(state.get("report", "").split())
        num_chunks = state.get("num_chunks", 0)
        num_sources = len(state.get("sources", []))
        num_pages = len(state.get("scraped_pages", []))

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card">
            <div class="metric-val">{elapsed:.0f}s</div>
            <div class="metric-lbl">Total time</div>
          </div>
          <div class="metric-card">
            <div class="metric-val">{num_pages}</div>
            <div class="metric-lbl">Pages scraped</div>
          </div>
          <div class="metric-card">
            <div class="metric-val">{num_chunks}</div>
            <div class="metric-lbl">Chunks indexed</div>
          </div>
          <div class="metric-card">
            <div class="metric-val">{num_sources}</div>
            <div class="metric-lbl">Sources cited</div>
          </div>
          <div class="metric-card">
            <div class="metric-val">{report_words:,}</div>
            <div class="metric-lbl">Report words</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs for each output
        tab_report, tab_feedback, tab_context, tab_search, tab_scraped = st.tabs([
            "📝 Report", "🧐 Critic Feedback", "📚 Retrieved Context", "🔍 Search Results", "📄 Scraped Pages"
        ])

        with tab_report:
            st.markdown(f"""
            <div class="panel">
              <div class="panel-header"><span class="dot" style="background:var(--accent)"></span>Final Report</div>
              <div class="panel-content report scroll-box">{state.get('report','—')}</div>
            </div>""", unsafe_allow_html=True)
            st.download_button(
                "⬇ Download report (.txt)",
                data=state.get("report", ""),
                file_name=f"research_{topic[:40].replace(' ','_')}.txt",
                mime="text/plain",
            )

        with tab_feedback:
            st.markdown(f"""
            <div class="panel">
              <div class="panel-header"><span class="dot" style="background:var(--warn)"></span>Critic Review</div>
              <div class="panel-content scroll-box">{state.get('feedback','—')}</div>
            </div>""", unsafe_allow_html=True)

        with tab_context:
            sources = state.get("sources", [])
            chips = "".join(
                f'<span class="source-chip"><b>[{i+1}]</b> {s}</span>' for i, s in enumerate(sources)
            ) or '<span class="source-chip">No sources retrieved</span>'
            st.markdown(f"""
            <div class="panel">
              <div class="panel-header"><span class="dot" style="background:var(--accent2)"></span>Retrieved Chunks (what the Writer actually saw)</div>
              <div style="margin-bottom:.9rem">{chips}</div>
              <div class="panel-content scroll-box">{state.get('retrieved_context','—')}</div>
            </div>""", unsafe_allow_html=True)

        with tab_search:
            st.markdown(f"""
            <div class="panel">
              <div class="panel-header"><span class="dot" style="background:var(--success)"></span>Search Agent Output</div>
              <div class="panel-content scroll-box">{state.get('search_results','—')}</div>
            </div>""", unsafe_allow_html=True)

        with tab_scraped:
            st.markdown(f"""
            <div class="panel">
              <div class="panel-header"><span class="dot" style="background:var(--accent2)"></span>Scraped Page Text (pre-chunking)</div>
              <div class="panel-content scroll-box">{state.get('scraped_content','—')}</div>
            </div>""", unsafe_allow_html=True)


# ── Empty state hint ───────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 1rem; color: #6B7A99;">
      <div style="font-size:3rem; margin-bottom:.8rem;">🔬</div>
      <div style="font-size:1rem;">Enter a topic above and click <strong style="color:#E8ECF4">Run Research</strong> to start the pipeline.</div>
    </div>
    """, unsafe_allow_html=True)
