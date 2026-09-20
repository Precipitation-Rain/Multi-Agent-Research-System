"""
Research Desk - Streamlit front end for the multi-agent research pipeline.

Run:  streamlit run app.py
Needs: streamlit >= 1.39
"""
import re
import time

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from agents import web_search_agent, scrape_url_agent, writer_chain, critics_chain

APP_NAME = "Research Desk"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="◐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Instrument+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');

:root{
  --bg:#060814; --text:#E8ECFA; --muted:#8B95B0; --faint:#5E6884;
  --glass:rgba(255,255,255,.045); --glass-2:rgba(255,255,255,.08);
  --edge:rgba(255,255,255,.10);
  --violet:#7C5CFF; --blue:#3B82F6; --cyan:#22D3EE;
  --ok:#34D399; --bad:#F87171; --warn:#FBBF24;
  --display:'Bricolage Grotesque', 'Instrument Sans', system-ui, sans-serif;
  --sans:'Instrument Sans', system-ui, -apple-system, sans-serif;
  --serif:'Newsreader', Georgia, serif;
}

/* ---------- canvas ---------- */
html, body, .stApp{ font-family:var(--sans); color:var(--text) !important; }
.stApp{
  background:
    radial-gradient(900px 520px at 10% -8%, rgba(124,92,255,.30), transparent 62%),
    radial-gradient(760px 460px at 96% 2%, rgba(34,211,238,.17), transparent 60%),
    radial-gradient(900px 600px at 50% 115%, rgba(59,130,246,.13), transparent 60%),
    var(--bg) !important;
}
.stApp::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
  background-size:56px 56px;
  -webkit-mask-image:radial-gradient(ellipse 70% 55% at 50% 0%, #000 30%, transparent 78%);
          mask-image:radial-gradient(ellipse 70% 55% at 50% 0%, #000 30%, transparent 78%);
}
[data-testid="stHeader"]{ background:transparent !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], footer{ display:none !important; }
.block-container{ max-width:980px !important; padding-top:2.4rem !important; padding-bottom:6rem !important;
                  position:relative; z-index:1; }

/* text colour on the dark canvas (report paper overrides below) */
.stApp [data-testid="stMarkdownContainer"] :is(p,li,h1,h2,h3,h4,h5,h6,span,strong,em,td,th,label){ color:var(--text) !important; }
.stApp a{ color:#8FB4FF !important; }

/* ---------- hero ---------- */
.brand{ display:flex; align-items:center; gap:.7rem; font-family:var(--display); font-weight:700;
        font-size:1.05rem; letter-spacing:-.01em; color:var(--text); margin-bottom:3.2rem; }
.brand .mark{ width:1.9rem; height:1.9rem; border-radius:10px;
        background:conic-gradient(from 210deg, var(--violet), var(--blue), var(--cyan), var(--violet));
        box-shadow:0 0 24px rgba(124,92,255,.55); position:relative; }
.brand .mark::after{ content:""; position:absolute; inset:5px; border-radius:6px; background:var(--bg); }
.hero{ font-family:var(--display); font-weight:700; font-size:clamp(2.6rem, 7vw, 4.6rem);
       line-height:1.0; letter-spacing:-.04em; margin:0 0 1.1rem 0;
       background:linear-gradient(180deg, #FFFFFF 15%, #9AA6CC 100%);
       -webkit-background-clip:text; background-clip:text; color:transparent; -webkit-text-fill-color:transparent; }
.lede{ font-size:1.12rem; line-height:1.6; color:var(--muted); max-width:36rem; margin:0 0 2.4rem 0; }

/* ---------- input ---------- */
[data-testid="stForm"]{ border:none !important; padding:0 !important; background:transparent !important; }
.stTextInput div[data-baseweb="base-input"]{ background:transparent !important; border:none !important; box-shadow:none !important; min-height:3.6rem; }
.stTextInput div[data-baseweb="input"], [data-testid="stTextInputRootElement"]{
  background:var(--glass) !important; border:1px solid var(--edge) !important; border-radius:16px !important;
  min-height:3.6rem; height:3.6rem; backdrop-filter:blur(14px); transition:border-color .2s, box-shadow .2s; box-shadow:none !important;
}
.stTextInput div[data-baseweb="input"]:focus-within, [data-testid="stTextInputRootElement"]:focus-within{
  border-color:rgba(124,92,255,.85) !important;
  box-shadow:0 0 0 4px rgba(124,92,255,.18), 0 10px 40px -10px rgba(124,92,255,.5) !important;
}
.stTextInput input{ background:transparent !important; font-family:var(--sans) !important; font-size:1.12rem !important;
  padding:1rem 1.2rem !important; color:var(--text) !important; -webkit-text-fill-color:var(--text) !important; caret-color:#fff; }
.stTextInput input::placeholder{ color:var(--faint) !important; -webkit-text-fill-color:var(--faint) !important; opacity:1; }
[data-testid="InputInstructions"]{ display:none !important; }
[data-testid="stForm"] .stElementContainer, [data-testid="stFormSubmitButton"], .stFormSubmitButton{ width:100% !important; }
.stFormSubmitButton > button, [data-testid="stFormSubmitButton"] > button{
  width:100% !important; height:3.6rem; border-radius:16px; border:none !important; color:#fff !important;
  font-family:var(--sans); font-weight:700; font-size:1.02rem; letter-spacing:.01em;
  background:linear-gradient(135deg, var(--violet) 0%, var(--blue) 55%, var(--cyan) 130%) !important;
  box-shadow:0 12px 34px -8px rgba(99,102,241,.75), inset 0 1px 0 rgba(255,255,255,.25);
  transition:transform .12s, box-shadow .2s, filter .2s;
}
.stFormSubmitButton > button:hover{ filter:brightness(1.1); box-shadow:0 16px 44px -8px rgba(99,102,241,.95), inset 0 1px 0 rgba(255,255,255,.3); }
.stFormSubmitButton > button:active{ transform:translateY(1px); }
.stFormSubmitButton > button p{ color:#fff !important; }

/* ---------- example chips ---------- */
.try-label{ font-size:.86rem; color:var(--faint); margin:1.3rem 0 .5rem 0; }
.st-key-chips button{ background:var(--glass) !important; border:1px solid var(--edge) !important; border-radius:999px !important;
  min-height:0; padding:.35rem 1rem; transition:border-color .2s, background .2s; }
.st-key-chips button p{ color:var(--muted) !important; font-size:.88rem; font-weight:500; }
.st-key-chips button:hover{ border-color:rgba(124,92,255,.7) !important; background:rgba(124,92,255,.12) !important; }
.st-key-chips button:hover p{ color:#fff !important; }

/* ---------- pipeline tracker ---------- */
.tracker{ display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; margin:3rem 0 1rem 0; }
.stage{ position:relative; overflow:hidden; padding:1.25rem 1.15rem 1.1rem; border-radius:20px;
        background:var(--glass); border:1px solid var(--edge); backdrop-filter:blur(14px);
        transition:border-color .3s, box-shadow .3s, opacity .3s; }
.stage.pending{ opacity:.55; }
.stage .icon{ width:2.5rem; height:2.5rem; border-radius:12px; display:grid; place-items:center;
        background:var(--glass-2); color:var(--muted); margin-bottom:1rem; }
.stage .icon svg{ width:1.3rem; height:1.3rem; fill:none; stroke:currentColor; stroke-width:1.8;
        stroke-linecap:round; stroke-linejoin:round; }
.sname{ font-family:var(--display); font-weight:700; font-size:1.12rem; letter-spacing:-.01em; color:var(--text); }
.sdesc{ font-size:.86rem; color:var(--muted); line-height:1.45; margin:.2rem 0 .95rem; min-height:2.5em; }
.smeta{ display:flex; align-items:center; justify-content:space-between; font-size:.8rem; color:var(--muted); }
.pill{ padding:.18rem .6rem; border-radius:999px; font-weight:600; background:var(--glass-2); color:var(--muted); }
.stage.running{ border-color:rgba(124,92,255,.7); box-shadow:0 0 0 1px rgba(124,92,255,.25), 0 18px 50px -18px rgba(124,92,255,.75); }
.stage.running .icon{ background:linear-gradient(135deg, var(--violet), var(--blue)); color:#fff; }
.stage.running .pill{ background:rgba(124,92,255,.22); color:#C4B5FF; }
.stage.running::after{ content:""; position:absolute; left:0; top:0; height:2px; width:40%;
        background:linear-gradient(90deg, transparent, var(--cyan), transparent); animation:sweep 1.6s linear infinite; }
@keyframes sweep{ from{ transform:translateX(-100%);} to{ transform:translateX(260%);} }
.stage.done{ border-color:rgba(52,211,153,.35); }
.stage.done .icon{ background:rgba(52,211,153,.16); color:var(--ok); }
.stage.done .pill{ background:rgba(52,211,153,.16); color:var(--ok); }
.stage.error{ border-color:rgba(248,113,113,.55); }
.stage.error .icon{ background:rgba(248,113,113,.16); color:var(--bad); }
.stage.error .pill{ background:rgba(248,113,113,.16); color:var(--bad); }
.bar{ height:3px; border-radius:3px; background:var(--glass-2); overflow:hidden; margin-bottom:1.4rem; }
.bar .fill{ height:100%; border-radius:3px; background:linear-gradient(90deg, var(--violet), var(--blue), var(--cyan));
        transition:width .5s ease; box-shadow:0 0 14px rgba(59,130,246,.8); }
@media (max-width:760px){ .tracker{ grid-template-columns:repeat(2, 1fr); } }
@media (prefers-reduced-motion:reduce){ .stage.running::after{ animation:none; } }

.notice{ display:block; padding:.75rem 1rem; margin:0 0 .6rem 0; border-radius:12px; font-size:.9rem;
         background:rgba(251,191,36,.08); border:1px solid rgba(251,191,36,.3); color:#FCD34D; }

/* ---------- result tiles ---------- */
.tiles{ display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin:.4rem 0 1.6rem 0; }
.tile{ padding:1.1rem 1.3rem; border-radius:18px; background:var(--glass); border:1px solid var(--edge); }
.tile .n{ font-family:var(--display); font-weight:700; font-size:2rem; letter-spacing:-.03em; color:var(--text); line-height:1.1; }
.tile .l{ font-size:.84rem; color:var(--muted); margin-top:.15rem; }
.topic-line{ font-family:var(--display); font-weight:600; font-size:1.05rem; color:var(--muted); margin:2rem 0 .9rem 0; }
.topic-line b{ color:var(--text); font-weight:600; }

/* ---------- tabs ---------- */
[role="tablist"]{ gap:4px !important; padding:5px !important; border-radius:14px; background:var(--glass);
        border:1px solid var(--edge); width:fit-content; max-width:100%; overflow-x:auto; }
[data-baseweb="tab-border"], [data-baseweb="tab-highlight"], .react-aria-SelectionIndicator{ display:none !important; }
[role="tab"]{ background:transparent !important; border-radius:10px !important; padding:.55rem 1.05rem !important; height:auto !important;
        border:none !important; cursor:pointer; }
[role="tab"] p{ color:var(--muted) !important; font-weight:600; font-size:.92rem; }
[role="tab"][aria-selected="true"]{ background:linear-gradient(135deg, rgba(124,92,255,.35), rgba(59,130,246,.25)) !important;
        box-shadow:inset 0 0 0 1px rgba(124,92,255,.5); }
[role="tab"][aria-selected="true"] p{ color:#fff !important; }

/* ---------- report paper ---------- */
.st-key-report{ background:#F9FAFD; border-radius:22px; padding:3rem clamp(1.3rem, 5vw, 3.6rem); margin-top:1.3rem;
        box-shadow:0 40px 90px -30px rgba(0,0,0,.85), 0 0 0 1px rgba(255,255,255,.6) inset; }
.st-key-report [data-testid="stMarkdownContainer"] :is(p,li,span,td,th,em,strong){ color:#1A2238 !important; }
.st-key-report [data-testid="stMarkdownContainer"] :is(p,li){ font-family:var(--serif); font-size:1.15rem; line-height:1.74; max-width:44rem; }
.st-key-report [data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4){ font-family:var(--display); color:#0B1226 !important; letter-spacing:-.025em; }
.st-key-report h1{ font-size:2.3rem; line-height:1.1; }
.st-key-report h2{ font-size:1.6rem; margin-top:2.2rem; }
.st-key-report h3{ font-size:1.22rem; }
.st-key-report a{ color:#3B4FE0 !important; }
.st-key-report code{ background:#ECEFF9 !important; color:#2B3A67 !important; }

.st-key-critic, .st-key-raw1, .st-key-raw2{ background:var(--glass); border:1px solid var(--edge); border-radius:20px;
        padding:1.8rem 2.1rem; margin-top:1.3rem; backdrop-filter:blur(14px); }
.st-key-critic{ border-left:3px solid var(--violet); }
.st-key-critic [data-testid="stMarkdownContainer"] :is(p,li){ font-size:1.02rem; line-height:1.7; }

.stApp pre, .stApp [data-testid="stCode"]{ background:#0A0F24 !important; border-radius:16px !important; border:1px solid var(--edge); }
.stApp pre code, .stApp pre span{ color:#C7D2F0 !important; background:transparent !important; }

.stDownloadButton > button{ border-radius:12px; border:1px solid var(--edge) !important; background:var(--glass) !important; margin-top:1rem; }
.stDownloadButton > button p{ color:var(--text) !important; font-weight:600; }
.stDownloadButton > button:hover{ border-color:rgba(124,92,255,.8) !important; background:rgba(124,92,255,.14) !important; }

[data-testid="stAlert"]{ background:rgba(248,113,113,.09) !important; border:1px solid rgba(248,113,113,.4) !important; border-radius:14px; }
[data-testid="stAlert"] *{ color:#FECACA !important; }

.empty{ text-align:center; padding:2.6rem 1rem; border:1px dashed var(--edge); border-radius:20px; color:var(--faint); font-size:.98rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
ICONS = {
    "search": '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    "scrape": '<svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2z"/><path d="M8 8h6M8 12h6"/></svg>',
    "write": '<svg viewBox="0 0 24 24"><path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 6l3 3"/></svg>',
    "review": '<svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 5-5"/></svg>',
}
STAGES = [
    ("search", "Search", "Finds recent, reliable sources"),
    ("scrape", "Read", "Opens the best source in full"),
    ("write", "Write", "Drafts the report"),
    ("review", "Review", "A critic checks the draft"),
]
STATUS_LABEL = {"pending": "Waiting", "running": "Working", "done": "Done", "error": "Failed"}
EXAMPLES = [
    "Solid-state batteries in electric cars",
    "How GLP-1 drugs are changing healthcare",
    "State of open-source LLMs",
]


def as_text(x) -> str:
    """Agents/chains can return str, message objects, or lists of content blocks."""
    x = getattr(x, "content", x)
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        parts = []
        for b in x:
            t = b.get("text", "") if isinstance(b, dict) else str(b)
            if t:
                parts.append(t)
        return "\n".join(parts)
    return str(x)


def tracker_html(status: dict, times: dict) -> str:
    cells, done, running = [], 0, 0
    for key, name, desc in STAGES:
        s = status[key]
        done += s == "done"
        running += s == "running"
        t = f"<span>{times[key]:.0f}s</span>" if key in times else ""
        cells.append(
            f'<div class="stage {s}"><div class="icon">{ICONS[key]}</div>'
            f'<div class="sname">{name}</div><div class="sdesc">{desc}</div>'
            f'<div class="smeta"><span class="pill">{STATUS_LABEL[s]}</span>{t}</div></div>'
        )
    pct = (done + 0.5 * running) / len(STAGES) * 100
    return (
        '<div class="tracker">' + "".join(cells) + "</div>"
        f'<div class="bar"><div class="fill" style="width:{pct:.0f}%"></div></div>'
    )


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "report"


def use_example(text: str):
    st.session_state.topic_input = text
    st.session_state.autorun = True


# ----------------------------------------------------------------------------
# Token-limit handling (e.g. Groq on-demand tier: 8,000 tokens per request/minute)
# ----------------------------------------------------------------------------
def is_limit_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(k in msg for k in (
        "413", "429", "rate_limit", "rate limit", "too large", "tokens per minute", "request too large"))


def wait_seconds(e: Exception):
    m = re.search(r"try again in\s*(?:(\d+)m)?\s*([\d.]+)(ms|s)", str(e))
    if not m:
        return None
    return int(m.group(1) or 0) * 60 + float(m.group(2)) / (1000 if m.group(3) == "ms" else 1)


def with_budget(fn, budget: int, notify, label: str, floor: int = 1200, attempts: int = 4):
    """
    Call fn(budget), where budget = how many characters of upstream text fn may send.
    On a token-limit error, shrink the budget and retry (waiting if the API says how long).
    """
    for n in range(attempts):
        try:
            return fn(budget)
        except Exception as e:
            if not is_limit_error(e) or n == attempts - 1:
                raise
            m = re.search(r"Limit (\d+), Requested (\d+)", str(e))
            factor = min(0.75, int(m.group(1)) / int(m.group(2)) * 0.75) if m else 0.6
            budget = max(floor, int(budget * factor))
            wait = wait_seconds(e)
            wait = min(wait + 1, 65) if wait else (0 if "413" in str(e) else 8)
            notify(f"{label}: hit the model's token limit. Retrying with a shorter input "
                   f"(about {budget:,} characters)" + (f" after {wait:.0f}s." if wait >= 1 else "."))
            if wait:
                time.sleep(wait)


# ----------------------------------------------------------------------------
# Pipeline (same four steps as pipeline.py, with live progress + limit handling)
# ----------------------------------------------------------------------------
def run_with_progress(topic: str, tracker_slot, notice_slot) -> None:
    keys = [k for k, _, _ in STAGES]
    status = {k: "pending" for k in keys}
    times: dict = {}
    notes: list = []
    state: dict = {}
    t_start = time.time()

    def paint():
        tracker_slot.markdown(tracker_html(status, times), unsafe_allow_html=True)
        st.session_state.tracker = (dict(status), dict(times))

    def notify(msg):
        notes.append(msg)
        notice_slot.markdown("".join(f'<div class="notice">{n}</div>' for n in notes), unsafe_allow_html=True)

    def step(key, fn):
        status[key] = "running"
        paint()
        t0 = time.time()
        try:
            out = fn()
        except Exception as e:
            status[key] = "error"
            paint()
            st.error(f"The {STAGES[keys.index(key)][1]} step failed: {e}")
            raise
        times[key] = time.time() - t0
        status[key] = "done"
        paint()
        return out

    try:
        # 1. search
        def do_search():
            def call(_):
                agent = web_search_agent()
                r = agent.invoke({"messages": [{"role": "user",
                    "content": f"Find recent, reliable, accurate information about: {topic}"}]})
                return as_text(r["messages"][-1].content)
            return with_budget(call, 1000, notify, "Search")

        state["search_results"] = step("search", do_search)

        # 2. read (scrape). If it cannot fit the token limit, continue with search results only.
        def do_scrape():
            def call(budget):
                agent = scrape_url_agent()
                r = agent.invoke({"messages": [{"role": "user", "content":
                    f"Based on the following research results about: '{topic}'\n"
                    f"Pick the most relevant url and scrape for deeper content.\n\n"
                    f"Search Results :\n {state['search_results'][:budget]}"}]})
                return as_text(r["messages"][-1].content)
            try:
                return with_budget(call, 6000, notify, "Read")
            except Exception as e:
                if is_limit_error(e):
                    notify("Read: the page was too large for the model's token limit, "
                           "so the report is based on the search results only.")
                    return "(Page content unavailable: it exceeded the model's token limit.)"
                raise

        state["scrape_results"] = step("scrape", do_scrape)

        # 3. write
        def do_write():
            def call(budget):
                research = (
                    f"SEARCH RESULTS : \n {state['search_results'][: budget // 2]} \n\n "
                    f"DETAILED SCRAPED CONTENT :  \n {state['scrape_results'][:budget]}"
                )
                return as_text(writer_chain.invoke({"topic": topic, "research": research}))
            return with_budget(call, 8000, notify, "Write")

        state["report"] = step("write", do_write)

        # 4. review
        def do_review():
            def call(budget):
                return as_text(critics_chain.invoke({"report": state["report"][:budget]}))
            return with_budget(call, 12000, notify, "Review")

        state["feedback"] = step("review", do_review)
    except Exception:
        st.session_state.result = None
        return

    state["elapsed"] = time.time() - t_start
    st.session_state.result = state
    st.session_state.topic_done = topic
    st.session_state.notes = notes


# ----------------------------------------------------------------------------
# Page
# ----------------------------------------------------------------------------
st.markdown(
    f'<div class="brand"><span class="mark"></span>{APP_NAME}</div>'
    '<h1 class="hero">Research anything.<br>Let the agents read.</h1>'
    '<p class="lede">Give a topic. Four agents find sources, read the best one in full, '
    'write a report and have a critic review it.</p>',
    unsafe_allow_html=True,
)

with st.form("topic_form"):
    c1, c2 = st.columns([5, 1.4], vertical_alignment="bottom")
    with c1:
        st.text_input(
            "Topic", key="topic_input", label_visibility="collapsed",
            placeholder="e.g. Impact of tariffs on Indian exports",
        )
    with c2:
        submitted = st.form_submit_button("Research", type="primary")

st.markdown('<div class="try-label">Or start with one of these</div>', unsafe_allow_html=True)
with st.container(key="chips"):
    cols = st.columns(len(EXAMPLES))
    for col, ex in zip(cols, EXAMPLES):
        col.button(ex, key=f"ex_{ex}", on_click=use_example, args=(ex,))

tracker_slot = st.empty()
notice_slot = st.empty()

run_requested = submitted or st.session_state.pop("autorun", False)
topic = (st.session_state.get("topic_input") or "").strip()

# tracker: idle, or repainted from the last run
if "tracker" in st.session_state and not run_requested:
    tracker_slot.markdown(tracker_html(*st.session_state.tracker), unsafe_allow_html=True)
    if st.session_state.get("notes"):
        notice_slot.markdown(
            "".join(f'<div class="notice">{n}</div>' for n in st.session_state.notes), unsafe_allow_html=True)
else:
    tracker_slot.markdown(tracker_html({k: "pending" for k, _, _ in STAGES}, {}), unsafe_allow_html=True)

if run_requested:
    if not topic:
        st.warning("Enter a topic to research.")
    else:
        st.session_state.pop("result", None)
        st.session_state.pop("notes", None)
        run_with_progress(topic, tracker_slot, notice_slot)

result = st.session_state.get("result")

if result and result.get("report"):
    done_topic = st.session_state.get("topic_done", "")
    words = len(result["report"].split())
    links = len(set(re.findall(r"https?://[^\s)\]>\"']+", result["search_results"])))
    elapsed = result.get("elapsed", 0)

    st.markdown(f'<div class="topic-line">Report on <b>{done_topic}</b></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tiles">'
        f'<div class="tile"><div class="n">{words:,}</div><div class="l">Words in the report</div></div>'
        f'<div class="tile"><div class="n">{links}</div><div class="l">Links found</div></div>'
        f'<div class="tile"><div class="n">{elapsed:.0f}s</div><div class="l">Total time</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    t_report, t_review, t_sources, t_page = st.tabs(
        ["Report", "Critic's review", "Sources found", "Page content"])

    with t_report:
        with st.container(key="report"):
            st.markdown(result["report"])
        st.download_button(
            "Download report (.md)", data=result["report"],
            file_name=f"{slug(done_topic)}.md", mime="text/markdown",
        )
    with t_review:
        with st.container(key="critic"):
            st.markdown(result["feedback"])
    with t_sources:
        with st.container(key="raw1"):
            st.markdown(result["search_results"])
    with t_page:
        with st.container(key="raw2"):
            st.markdown(result["scrape_results"])
elif not run_requested:
    st.markdown('<div class="empty">Your report, the critic\'s review and the sources will appear here.</div>',
                unsafe_allow_html=True)